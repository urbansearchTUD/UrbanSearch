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
    _driver = GraphDatabase.driver(config.get('neo4j', 'bolt_uri'),
                                   auth=basic_auth(config.get('neo4j', 'username'), config.get('neo4j', 'password')))
    return _driver.session()


def _get_cities():
    global _cities
    if _cities:
        return _cities
    else:
        with _get_session() as session:
            # Records need to be copied due to the scope of the session variable
            _cities = [c for c in session.run('MATCH (a:City) RETURN a')]
            return _cities


def _city_by_name(name):
    # Using generators, find the city matching the given name
    return next(c for c in _get_cities() if _city_property(c, 'name') == name)


def _city_property(city, property_name):
    # Returns the property belonging to a node. Neo4j uses 'a' in Record objects for nodes.
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
    Calculates the relative distance between two cities A and B, calculated using Pythagorem on the
    latitude and longitude difference between the cities.

    :param name_a: The name of city A
    :param name_b: The name of city B
    :return: The relative distance
    """
    city_a = _city_by_name(name_a)
    city_b = _city_by_name(name_b)

    lat_diff = _city_property(city_a, 'latitude') - _city_property(city_b, 'latitude')
    lon_diff = _city_property(city_a, 'longitude') - _city_property(city_b, 'longitude')

    return math.sqrt(lat_diff ** 2 + lon_diff ** 2)


def city_haversine_distance(name_a, name_b):
    """
    Calculates the haversine distance between two cities, in kilometres.

    The haversine distance in this case is the absolute distance between two cities, taking into account
    the fact that Earth is a sphere.

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
    Stores the provided index in Neo4j and creates relationships to all cities that occur in the document.
    If a list of topics is provided, it also labels the index node with every topic.

    The index should be a dictionary, containing at least:

    `filename`: The location of the page pointed to
    `offset`: The offset of the page
    `length`: The content length of the page

    :param index: The index dictionary
    :param co_occurrences: A list of tuples, containing co-occurrences (e.g. `[('Amsterdam', 'Rotterdam')]`)
    :param topics A list of topics. Defaults to None
    :return: True iff the index has been successfully stored
    """
    # FIXME: duplicate city names -> only insert largest? if so, might as well remove duplicates completely
    # FIXME: current situation: insert both

    # Create a set of cities to remove duplicates
    cities = {city for occurrence in co_occurrences for city in occurrence}

    # Query needs the following parameters:
    # City name 1, City name 2, string in syntax ':Topic1:Topic2:Topic3', int offset, int length

    # Join all topics with ':', also add a leading ':' because there always is an Index label
    topics = ':{}'.format(':'.join(topic.capitalize() for topic in topics)) if topics else ''

    # Match cities by name and name results c<num>
    match_query = '\n'.join('MATCH (c{0}:City {{ name: "{1}" }})'.format(i, city) for i, city in enumerate(cities))

    # Create a node for the index if it doesn't exist
    merge_query = 'MERGE (i:Index{0} {{ filename: "{1}", offset: {2}, length: {3} }})'.format(topics, index['filename'],
                                                                                              index['offset'],
                                                                                              index['length'])

    # Create unique relations from city c<num> to the index
    create_query = 'CREATE UNIQUE {0}'.format(
        ', '.join('(c{0})-[r{0}:OCCURS_IN]->(i)'.format(i) for i in range(len(cities))))

    # Return the ids of the created relations
    return_query = 'RETURN {0}'.format(', '.join('ID(c{0}) AS id{0}'.format(i) for i in range(len(cities))))

    query = '{0}\n{1}\n{2}\n{3}'.format(match_query, merge_query, create_query, return_query)

    results = perform_query(query)

    logger.debug('Constructed query: {}'.format(query))
    logger.debug('Query resulted in:\n{}'.format(', '.join(rel_id for result in results for rel_id in result)))

    return len(results) > 0
