import math
import logging
from neo4j.v1 import (basic_auth, GraphDatabase, SessionError,
                      CypherSyntaxError, DriverError, ServiceUnavailable)

import config

CATEGORIES = config.get('score', 'categories')
DEFAULT_CAT_DICT = dict.fromkeys(CATEGORIES, 0)
RELATES_TO = config.get('neo4j', 'relates_to_name')
OCCURS_IN = config.get('neo4j', 'occurs_in_name')

_logger = logging.getLogger('db_utils')
_driver = GraphDatabase.driver(
    config.get('neo4j', 'bolt_uri'),
    auth=basic_auth(config.get('neo4j', 'username'),
                    config.get('neo4j', 'password')))

_cities = None


def connected_to_db():
    """
    Verifies the database is still accepting connections

    :return: True iff the database is available
    """
    try:
        with _driver.session():
            return True
    except (DriverError, SessionError, ServiceUnavailable):
        return False


def _run(runner, query, *params, **kwparams):
    # Runs the given query with given parameters, either as
    # single transaction (if runner is a Session object)
    # or within a single transaction, if runner is a Transaction
    # object.
    try:
        return [r for r in runner.run(query, *params, **kwparams)]
    except (CypherSyntaxError, SessionError) as e:
        _logger.error('query {}\nraised: {}'.format(query, e))


def perform_queries(queries, params):
    """
    Performs the given queries with given parameters, in a single
    transaction.

    :param queries: A list of queries
    :param params: A list of lists of parameters belonging to the queries
    :return: A list of result lists
    """
    with _driver.session() as session:
        with session.begin_transaction() as tx:
            return [[r for r in _run(tx, queries[i], params[i])]
                    for i in range(len(queries))]


def perform_query(query, *params, **kwparams):
    """
    Performs the given query with given parameters, either as an expanded
    list or an expanded dictionary.

    :param query: The query to perform
    :param params: The query parameters, as positional arguments
    :param kwparams: The query parameters, as key value pairs
    :return: A list of resulting records
    """
    with _driver.session() as session:
        return _run(session, query, *params, **kwparams)


def _store_ic_rel_query(city_a, city_b):
    # Generates a query for storing an intercity relation
    # Returns a query, params tuple
    query = '''
        MATCH (a:City {{ name: $a }})
        MATCH (b:City {{ name: $b }})
        MERGE (a)<-[r:{0}]-(b)
        ON CREATE SET r = {{ {1} }}
    '''.format(RELATES_TO, ', '.join('{0}: $val'.format(p)
                                     for p in CATEGORIES))
    return query, {'a': city_a, 'b': city_b, 'val': 0}


def store_ic_rel(city_a, city_b):
    """
    Stores a relation between the given cities and initialises the
    scores for all topics to 0.

    :param city_a: City A
    :param city_b: City B
    :return: True iff stored successfully
    """
    query, params = _store_ic_rel_query(city_a, city_b)
    return perform_query(query, params) == []


def store_ic_rels(pairs):
    """
    Same as store_ic_rel, but for multiple city pairs

    :param pairs: A list of city tuples
    :return: True iff all pairs have been successfully stored
    """
    query_list = list()
    params_list = list()

    for pair in pairs:
        query, params = _store_ic_rel_query(pair[0], pair[1])
        query_list.append(query)
        params_list.append(params)

    return len(perform_queries(query_list, params_list)) == len(query_list)


def _store_index_query(index):
    # Generates a query for storing an index
    # Returns a query, params tuple
    query = '''
        MERGE (i:Index {{ digest: $digest }})
        ON CREATE SET i = {{ {0}, {1} }}
    '''.format(', '.join('{0}: ${0}'.format(k) for k in index.keys()),
               ', '.join('{0}: 0'.format(k) for k in CATEGORIES))
    return query, {k: v for k, v in index.items()}


def store_index(index):
    """
    Stores the provided index. The index should be a dictionary,
    containing:

    `digest`: A unique string to identify the index with
    `digest`: The location of the page pointed to
    `offset`: The offset of the page
    `length`: The content length of the page

    :param index: The index dictionary
    :return: True iff the index has been successfully stored
    """
    return perform_query(*_store_index_query(index)) == []


def store_indices(indices):
    """
    Same as store_index but for multiple indices"

    :param indices: The indices to create
    :return: True iff created successfully
    """
    query_list = list()
    params_list = list()

    for index in indices:
        query, params = _store_index_query(index)
        query_list.append(query)
        params_list.append(params)

    return len(perform_queries(query_list, params_list)) == len(query_list)


def _store_occurrence_query(digest, city):
    # Generates a query for storing an occurrence, as a relation
    # between a city and an index. Returns a query, params tuple
    query = '''
        MATCH (i:Index {{ digest: $digest }})
        MATCH (a:City {{ name: $city }})
        MERGE (a)-[:{0}]->(i)
    '''.format(OCCURS_IN)
    return query, {'digest': digest, 'city': city}


def store_occurrence(digest, city):
    """
    Creates a relation between the given index and city

    :param digest: The unique identifier of the index
    :param city: The name of the city
    :return: True iff stored successfully
    """
    return perform_query(*_store_occurrence_query(digest, city)) == []


def store_occurrences(digests, occurrences):
    """
    Same as store_occurrence but for multple indices/occurrences.
    Allows for duplicate index digests to be able to store multiple
    occurrences.

    :param digests: The unique identifiers of the indices
    :param occurrences: The names of the cities
    :return: True iff stored successfully
    """
    query_list = list()
    params_list = list()

    for i, fn in enumerate(digests):
        query, params = _store_occurrence_query(fn, occurrences[i])
        query_list.append(query)
        params_list.append(params)

    return len(perform_queries(query_list, params_list)) == len(query_list)


def _store_index_topics_query(digest, topics):
    # Generates a query for storing index topics, as labels
    # Topics must be set or a None, None tuple is returned.
    # Returns a query, params tuple
    if not topics:
        return None, None
    query = '''
        MATCH (i:Index {{ digest: $digest }})
        SET i{}
    '''.format(':{}'.format(':'.join(t.capitalize() for t in topics)))
    return query, {'digest': digest}


def store_index_topics(digest, topics):
    """
    Appends the given topics as labels to the given index.

    Caution: the index must already exist in the database!

    :param digest: The unique identifier of the index
    :param topics: A list of topics
    :return: True iff the topics have been successfully stored
    """
    query, params = _store_index_topics_query(digest, topics)
    if query:
        return perform_query(query, params) == []


def store_indices_topics(digests, topics):
    """
    Same as store_index_topics, but for multiple indices.

    :param digests: The unique identifiers of the indices
    :param topics: A list of topic lists
    :return: True iff the topics have been successfully stored
    """
    query_list = list()
    params_list = list()

    for i, fn in enumerate(digests):
        query, params = _store_index_topics_query(fn, topics[i])
        if query:
            query_list.append(query)
            params_list.append(params)

    return len(perform_queries(query_list, params_list)) == len(query_list)


def _store_index_probabilities_query(digest, probabilities):
    # Generates a query for storing topic probabilities on an index
    # Default probabilities (0) are used if none are provided
    # Returns a query, params tuple
    if not probabilities:
        probabilities = DEFAULT_CAT_DICT

    query = '''
        MATCH (i:Index {{ digest: $digest }})
        SET {}
    '''.format(','.join('i.{0}=${0}'.format(k) for k in probabilities.keys()))
    return query, {'digest': digest, **probabilities}


def store_index_probabilities(digest, probabilities=None):
    """
    Stores topic probabilities in the given Index node. The probabilities
    parameter is a dictionary and it's values default to 0.
    The following probability types are supported by default:

    - commuting
    - shopping
    - leisure
    - moving
    - education
    - collaboration
    - transportation
    - other

    :param digest: The unique identifier of the index
    :param probabilities: A dictionary of topic:probability pairs
    :return: True iff the probabilities have been successfully stored
    """
    query, params = _store_index_probabilities_query(digest, probabilities)
    return perform_query(query, params) == []


def store_indices_probabilities(digests, probabilities):
    """
    Same as store_index_probabilities, but for multiple indices.

    :param digests: A list of unique identifiers
    :param probabilities: A list of probability dictionaries per index
    :return: True iff stored successfully
    """
    query_list = list()
    params_list = list()

    for i, fn in enumerate(digests):
        query, params = _store_index_probabilities_query(fn, probabilities[i])
        query_list.append(query)
        params_list.append(params)

    return len(perform_queries(query_list, params_list)) == len(query_list)


def _get_ic_rel_query(city_a, city_b):
    # Generates a query for retrieving intercity relation statistics
    # Returns a query, params tuple
    query = '''
        MATCH (a:City {{name: $city_a}})-[r:{0}]-(b:City {{name: $city_b}})
        RETURN properties(r) AS relation
    '''.format(RELATES_TO)
    return query, {'city_a': city_a, 'city_b': city_b}


def _parse_ic_rel_result(result):
    # Checks the result and returns a dictionary of the relation scores
    if result:
        return {k: v for k, v in result[0]['relation'].items()}


def get_ic_rel(city_a, city_b):
    """
    Retrieves the relation scores between City A and City B

    :param city_a: City A
    :param city_b: City B
    :return: A dictionary containing the scores per topic
    """
    result = perform_query(*_get_ic_rel_query(city_a, city_b))
    return _parse_ic_rel_result(result)


def get_ic_rels(city_pairs):
    """
    Retrieves the relation scores between the given pairs of cities.

    :param city_pairs: A list of tuples of cities
    :return: A list of dictionaries, containing the scores per city pair
    """
    query_list = list()
    params_list = list()

    for pair in city_pairs:
        query, params = _get_ic_rel_query(pair[0], pair[1])
        query_list.append(query)
        params_list.append(params)

    return [_parse_ic_rel_result(r)
            for r in perform_queries(query_list, params_list)]


def _get_index_probabilities_query(digest):
    # Generates a query for retrieving index probabilities
    # Returns a query, params tuple
    query = '''
        MATCH (i:Index {{ digest: $digest }})
        RETURN {}
    '''.format(', '.join('i.{0} AS {0}'.format(p) for p in CATEGORIES))
    return query, {'digest': digest}


def _parse_index_probabilities_result(result):
    # Checks the result and returns a dictionary of topic-probability pairs
    if result:
        return {k: v for k, v in result[0].items()}


def get_index_probabilities(digest):
    """
    Returns a dictionary of topic probabilities for the given index

    :param digest: A unique identifier representing an index
    :return: The dictionary of topic probabilities
    """
    result = perform_query(*_get_index_probabilities_query(digest))
    return _parse_index_probabilities_result(result)


def get_indices_probabilities(digests):
    """
    Retrieves the topic probabilities of the given indices

    :param digests: A list of unique identifiers, representing indices
    :return: A list of dictionaries, containing the probabilities per
    topic per index
    """
    query_list = list()
    params_list = list()

    for digest in digests:
        query, params = _get_index_probabilities_query(digest)
        query_list.append(query)
        params_list.append(params)

    return [_parse_index_probabilities_result(r)
            for r in perform_queries(query_list, params_list)]


def _get_index_topics_query(digest):
    # Generates a query for retrieving index topics
    # Returns a query, params tuple
    query = '''
        MATCH (i:Index { digest: $digest })
        RETURN labels(i) AS labels
    '''
    return query, {'digest': digest}


def _parse_index_topics_result(result):
    # Checks the result and returns a list of topics
    if result:
        return [label for label in result[0]['labels'] if label != 'Index']


def get_index_topics(digest):
    """
    Retrieves a list of topics for a given index.

    :param digest: A unique identifier, representing an index
    :return: A list of topics
    """
    result = perform_query(*_get_index_topics_query(digest))
    return _parse_index_topics_result(result)


def get_indices_topics(digests):
    """
    Retrieves a list of topics per given index.

    :param digests: A list of unique identifiers, representing the indices
    :return: A list of topic lists
    """
    query_list = list()
    params_list = list()

    for digest in digests:
        query, params = _get_index_topics_query(digest)
        query_list.append(query)
        params_list.append(params)

    return [_parse_index_topics_result(r)
            for r in perform_queries(query_list, params_list)]


def _get_cities():
    # Returns a list of Neo4j City objects. Tries to reuse them
    # save database hits
    global _cities

    if not _cities:
        _cities = [c for c in perform_query('MATCH (a:City) RETURN a')]

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
