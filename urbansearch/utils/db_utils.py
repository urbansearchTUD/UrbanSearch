import logging
import math

from neo4j.v1 import GraphDatabase, basic_auth, SessionError, CypherSyntaxError

import config

TOPIC_PROBS = {
    'commuting': 0,
    'shopping': 0,
    'leisure': 0,
    'moving': 0,
    'education': 0,
    'collaboration': 0,
    'transportation': 0,
    'other': 0
}

# Keep a global driver
_driver = None
# Keep a global list of cities to prevent too many DB hits
_cities = None

logger = logging.getLogger(__name__)


def _get_session():
    global _driver

    if _driver:
        return _driver.session()

    # If no driver is present, create a new one
    _driver = GraphDatabase.driver(
        config.get('neo4j', 'bolt_uri'),
        auth=basic_auth(config.get('neo4j', 'username'),
                        config.get('neo4j', 'password')))
    return _driver.session()


def _get_cities():
    global _cities
    if _cities:
        return _cities
    else:
        with _get_session() as session:
            # Records need to be copied
            # due to the scope of the session variable
            _cities = [c for c in session.run('MATCH (a:City) RETURN a')]
            return _cities


def _city_by_name(name):
    # Using generators, find the city matching the given name
    return next(c for c in _get_cities() if _city_property(c, 'name') == name)


def _city_property(city, property_name):
    # Returns the property belonging to a node.
    # Neo4j uses 'a' in Record objects for nodes.
    # Tries to cast the property to float and falls back to strings.
    try:
        return float(city['a'].properties[property_name])
    except ValueError:
        return city['a'].properties[property_name]


def _get_topic_str(topics):
    # Join all topics with ':', also add a leading ':'
    # because there always is an Index label
    return ':{}'.format(':'.join(topic.capitalize() for topic in topics))


def _get_property_ret_str(name='r', properties=TOPIC_PROBS):
    return ', '.join('{0}.{1} AS {1}'.format(name, k) for k in
                     properties.keys())


def _get_property_kv_str(properties=TOPIC_PROBS):
    return ', '.join('{}: {}'.format(k, v) for k, v in properties.items())


def _get_property_set_str(name='r', properties=TOPIC_PROBS):
    return ', '.join('{}.{} = {}'.format(name, k, v)
                     for k, v in properties.items())


def perform_query(query):
    """
    Utility method to run an arbitrary query.

    Use with caution!

    :param query: The query to execute
    :return: The result of the query, as provided by Neo4j
    """
    try:
        with _get_session() as session:
            return [r for r in session.run(query)]
    except (CypherSyntaxError, SessionError) as e:
        logger.error('query: %s\nraised error: %s' % (query, e))
        return None


def city_names():
    """
    Returns a list of city names. Tries to cache the cities whenever possible.
    :return: A list of city names, as retrieved from Neo4j
    """
    return [_city_property(city, 'name') for city in _get_cities()]


def city_population(name):
    """
    Returns the populaton of a given city
    :param name: The name of the city to look up
    :return: The population of the given city
    """
    return int(_city_property(_city_by_name(name), 'population'))


def city_distance(name_a, name_b):
    """
    Calculates the relative distance between two cities A and B,
    calculated using Pythagorem on the
    latitude and longitude difference between the cities.

    :param name_a: The name of city A
    :param name_b: The name of city B
    :return: The relative distance
    """
    city_a = _city_by_name(name_a)
    city_b = _city_by_name(name_b)

    lat_diff = _city_property(
        city_a, 'latitude') - _city_property(city_b, 'latitude')
    lon_diff = _city_property(
        city_a, 'longitude') - _city_property(city_b, 'longitude')

    return math.sqrt(lat_diff ** 2 + lon_diff ** 2)


def city_haversine_distance(name_a, name_b):
    """
    Calculates the haversine distance between two cities, in kilometres.

    The haversine distance in this case is
    the absolute distance between two cities,
    taking into account the fact that Earth is a sphere.

    :param name_a: The name of city A
    :param name_b: The name of city B
    :return: The haversine distance between city A and city B
    """
    city_a = _city_by_name(name_a)
    city_b = _city_by_name(name_b)

    deg_to_rad = math.pi / 180
    lat_a = _city_property(city_a, 'latitude')
    lat_b = _city_property(city_b, 'latitude')
    lon_a = _city_property(city_a, 'longitude')
    lon_b = _city_property(city_b, 'longitude')

    a = 0.5 - math.cos((lat_a - lat_b) * deg_to_rad) / 2 + \
        math.cos(lat_a * deg_to_rad) * math.cos(lat_b * deg_to_rad) \
        * (1 - math.cos((lon_a - lon_b) * deg_to_rad)) / 2

    # 6371 = Earth's radius
    return 2 * 6371 * math.asin(math.sqrt(a))


def get_ic_rel(city_a, city_b, rel_name='RELATES_TO'):
    """
    Retrieves the relation scores for city A and city B, as a dictionary.
    See `store_ic_rel` for a list of supported categories.

    :param city_a: The name of city A
    :param city_b: The name of city B
    :param rel_name: The name of the relation. Defaults to 'RELATES_TO'.
    Should not be adjusted in normal cases.
    :return: A dictionary containing the relationship scores for different
    categories or None if no relation exists.
    """
    query = '''
        MATCH (n:City) WHERE n.name = '{0}'
        MATCH (m:City) WHERE m.name = '{1}'
        MATCH (n)-[r:{2}]-(m)
        RETURN {3}
        '''.format(city_a, city_b, rel_name, _get_property_ret_str())

    result = perform_query(query)
    return {k: v for k, v in result[0].items()} if result else None


def get_index_probabilities(index):
    """
    Returns the probabilities for all topics that a given index belongs to
    that topic.
    :param index: The filename of the index
    :return: A dictionary of `topic: probability` pairs or None if no topics
    belong to the index
    """
    query = '''
        MATCH (i:Index) WHERE i.filename = '{0}'
        RETURN {1}
    '''.format(index, _get_property_ret_str(name='i'))

    result = perform_query(query)
    return {k: v for k, v in result[0].items()} if result else {}


def store_index(index, co_occurrences):
    """
    Stores the provided index in Neo4j and creates relationships
    to all cities that occur in the document.

    The index should be a dictionary, containing at least:

    `filename`: The location of the page pointed to
    `offset`: The offset of the page
    `length`: The content length of the page

    :param index: The index dictionary
    :param co_occurrences: A list of tuples,
           containing co-occurrences (e.g. `[('Amsterdam', 'Rotterdam')]`)
    :return: True iff the index has been successfully stored
    """
    # Create a set of cities to remove duplicates
    cities = {city for occurrence in co_occurrences for city in occurrence}
    topic_probabilities = _get_property_kv_str()

    # Create a node for the index if it doesn't exist
    index_result = perform_query('''
        MERGE (i:Index {{ filename: '{0}', offset: {1}, length: {2}, {3} }})
        RETURN ID(i) AS id
    '''.format(index['filename'], index['offset'], index['length'],
               topic_probabilities))

    index_id = index_result[0]['id']

    # For every city in the co-occurrence list,
    # create a relationship to the index node
    created_relations = []
    for city in cities:
        create_relation_result = perform_query('''
            MATCH (i:Index) WHERE ID(i)={0}
            MATCH (c:City {{ name: '{1}' }})
            MERGE (c)-[r:OCCURS_IN]-(i)
            RETURN ID(r) AS id
        '''.format(index_id, city))
        created_relations.append(create_relation_result[0]['id'])

    return len(created_relations) == len(cities)


def store_index_topics(index, topics):
    """
    Appends the given topics as labels to the given index.

    Caution: the index must already exist in the database!

    :param index: The filename of the index
    :param topics: A list of topics
    :return: True iff the topics have been successfully stored
    """
    if not topics:
        return False

    query = '''
        MATCH (i:Index {{ filename: '{}' }})
        SET i{}
        RETURN ID(i) AS id
    '''.format(index, _get_topic_str(topics))

    return 'id' in perform_query(query)[0]


def store_index_probabilities(index, probabilities):
    """
    Stores topic probabilities in the given Index node. The probabilities
    parameter is a dictionary and it's values default to 0.
    The following probability types are supported:

    - commuting
    - shopping
    - leisure
    - moving
    - education
    - collaboration
    - transportation
    - other

    :param index: The name of the index
    :param probabilities: A dictionary of topic:probability pairs
    :return: True iff the probabilities have been successfully stored
    :raises ValueError iff the passed scores dict contains a non-existing
    score type
    """
    current = get_index_probabilities(index)

    if probabilities:
        # Fill in the passed scores
        probabilities = {**TOPIC_PROBS, **current, **probabilities}

        if len(probabilities) > len(TOPIC_PROBS):
            raise ValueError('Invalid score type given!')
    else:
        probabilities = TOPIC_PROBS

    query = '''
        MATCH (i:Index) WHERE i.filename = '{0}'
        SET {1}
        RETURN ID(i) AS id
    '''.format(index, _get_property_set_str(name='i',
                                            properties=probabilities))
    return 'id' in perform_query(query)[0]


def store_ic_rel(city_a, city_b, rel_name='RELATES_TO'):
    """
    Stores a relationship from city A to city B with default scores.
    If the relationship already exists and if any scores exist, they are
    overwritten.

    :param city_a: The name of city A
    :param city_b: The name of city B
    :param rel_name: The name of the relation, defaulting to 'RELATES_TO'.
        Should not need to be adjusted in normal cases.
    :return: True iff the intercity relation has been succesfully stored
    """
    query = '''
        MATCH (a:City {{ name: '{0}' }})
        MATCH (b:City {{ name: '{1}' }})
        MERGE (a)-[r:{2} {{ {3} }}]-(b)
        RETURN ID(r) AS id
    '''.format(city_a, city_b, rel_name, _get_property_kv_str())

    return 'id' in perform_query(query)[0]
