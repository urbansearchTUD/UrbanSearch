import logging
import math

from neo4j.v1 import GraphDatabase, basic_auth, SessionError, CypherSyntaxError

import config

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


def store_index(index, co_occurrences, topics=None):
    """
    Stores the provided index in Neo4j and creates relationships
    to all cities that occur in the document.
    If a list of topics is provided,
    it also labels the index node with every topic.

    The index should be a dictionary, containing at least:

    `filename`: The location of the page pointed to
    `offset`: The offset of the page
    `length`: The content length of the page

    :param index: The index dictionary
    :param co_occurrences: A list of tuples,
           containing co-occurrences (e.g. `[('Amsterdam', 'Rotterdam')]`)
    :param topics A list of topics. Defaults to None
    :return: True iff the index has been successfully stored
    """
    # Create a set of cities to remove duplicates
    cities = {city for occurrence in co_occurrences for city in occurrence}

    # Join all topics with ':', also add a leading ':'
    # because there always is an Index label
    topics = _join_topics(topics) if topics else ''

    # Create a node for the index if it doesn't exist
    index_result = perform_query('''
        MERGE (i:Index{0} {{ filename: '{1}', offset: {2}, length: {3} }})
        RETURN ID(i) AS id
    '''.format(topics, index['filename'], index['offset'], index['length']))
    index_id = index_result[0]['id']

    # For every city in the co-occurrence list,
    # create a relationship to the index node
    created_relations = []
    for city in cities:
        create_relation_result = perform_query('''
            MATCH (i:Index) WHERE ID(i)={0}
            MATCH (c:City {{ name: "{1}" }})
            MERGE (c)-[r:OCCURS_IN]-(i)
            RETURN ID(r) AS id
        '''.format(index_id, city))
        created_relations.append(create_relation_result[0]['id'])

    return len(created_relations) == len(cities)


def _join_topics(topics):
    # Join all topics with ':', also add a leading ':'
    # because there always is an Index label
    # To limit branch points a second method is made for this.
    return ':{}'.format(':'.join(topic.capitalize() for topic in topics))


def _get_default_ic_rel_dict():
    # Returns a default dictionary containing the supported categories.
    return {
        'commuting': -1,
        'shopping': -1,
        'leisure': -1,
        'moving': -1,
        'business': -1,
        'education': -1,
        'collaboration': -1,
        'transportation': -1,
        'other': -1
    }


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
    property_str = ', '.join('r.{0} AS {0}'.format(k) for k in
                             _get_default_ic_rel_dict().keys())
    query = '''
        MATCH (n:City) WHERE n.name = '{0}'
        MATCH (m:City) WHERE m.name = '{1}'
        MATCH (n)-[r:{2}]-(m)
        RETURN {3}
        '''.format(city_a, city_b, rel_name, property_str)

    result = perform_query(query)
    return {k: v for k, v in result[0].items()} if result else None


def store_ic_rel(city_a, city_b, scores=None, rel_name='RELATES_TO'):
    """
    Stores a relationship from city A to city B with given scores.
    If any scores exist, they are updated, preserving any existing scores
    that are not being updated.

    The scores parameter is a dictionary and it's values default to -1.
    The following score types are supported:

    - commuting
    - shopping
    - leisure
    - moving
    - business
    - education
    - collaboration
    - transportation
    - other

    :param city_a: The name of city A
    :param city_b: The name of city B
    :param scores: A dictionary of scores, with each score defaulting to -1
    :param rel_name: The name of the relation, defaulting to 'RELATES_TO'.
        Should not need to be adjusted in normal cases.
    :return: True iff the intercity relation has been succesfully stored
    :raises ValueError iff the passed scores dict contains a non-existing
    score type
    """
    default_scores = _get_default_ic_rel_dict()
    current_scores = get_ic_rel(city_a, city_b, rel_name)

    if scores:
        # Fill in the passed scores
        if current_scores:
            scores = {**default_scores, **current_scores, **scores}
        else:
            scores = {**default_scores, **scores}

        if len(scores) > len(default_scores):
            raise ValueError('Invalid score type given!')
    else:
        scores = default_scores

    # Convert to comma separated string
    scores = ', '.join('{0}: {1}'.format(k, v) for k, v in scores.items())

    rel_query = """
        MATCH (a:City {{ name: '{0}' }})
        MATCH (b:City {{ name: '{1}' }})
        MERGE (a)-[r:{2} {{ {3} }}]-(b)
        RETURN ID(r) AS id
    """.format(city_a, city_b, rel_name, scores)

    logger.debug(rel_query)

    return 'id' in perform_query(rel_query)[0]
