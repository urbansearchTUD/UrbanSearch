import math
import logging
from neo4j.v1 import (basic_auth, GraphDatabase, SessionError,
                      CypherSyntaxError, DriverError, ClientError,
                      ServiceUnavailable)

import config

CATEGORIES = config.get('score', 'categories')
CAT_NO_OTHER = list(CATEGORIES)
CAT_NO_OTHER.remove('other')
DEFAULT_CAT_DICT = dict.fromkeys(CATEGORIES, 0)
DEFAULT_CAT_DICT_NO_OTHER = dict.fromkeys(CAT_NO_OTHER, 0)
DEFAULT_SCORE_DICT = {'total': 0, **DEFAULT_CAT_DICT}
RELATES_TO = config.get('neo4j', 'relates_to_name')
OCCURS_IN = config.get('neo4j', 'occurs_in_name')

_logger = logging.getLogger(__name__)
_driver = GraphDatabase.driver(
    config.get('neo4j', 'bolt_uri'),
    auth=basic_auth(config.get('neo4j', 'username'),
                    config.get('neo4j', 'password')),
    encrypted=False)

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
    except (ClientError, CypherSyntaxError, SessionError) as e:
        _logger.error('query {}\nraised: {}'.format(query, e))


def perform_queries(queries, params, access_mode='write'):
    """
    Performs the given queries with given parameters, in a single
    transaction.

    :param queries: A list of queries
    :param params: A list of lists of parameters belonging to the queries
    :return: A list of result lists
    """
    with _driver.session(access_mode=access_mode) as session:
        with session.begin_transaction() as tx:
            return [[r for r in _run(tx, queries[i], params[i])]
                    for i in range(len(queries))]


def perform_query(query, *params, access_mode='write', **kwparams):
    """
    Performs the given query with given parameters, either as an expanded
    list or an expanded dictionary.

    :param query: The query to perform
    :param params: The query parameters, as positional arguments
    :param kwparams: The query parameters, as key value pairs
    :return: A list of resulting records
    """
    with _driver.session(access_mode=access_mode) as session:
        return _run(session, query, *params, **kwparams)


def _store_ic_rel_query(city_a, city_b, values=None):
    # Generates a query for storing an intercity relation
    # Returns a query, params tuple
    if not values:
        values = DEFAULT_SCORE_DICT
    else:
        values = {**DEFAULT_SCORE_DICT, **values}
        values['total'] = sum(values.values())
    query = '''
        MATCH (a:City {{ name: $a }})
        MATCH (b:City {{ name: $b }})
        MERGE (a)-[r:{0}]->(b)
        ON CREATE SET r = {{ {1} }}
        ON MATCH SET {2}
    '''.format(RELATES_TO, ', '.join('{0}: ${0}'.format(v)
                                     for v in values.keys()),
               ', '.join('r.{0}=${0}'.format(v) for v in values.keys()))
    return query, {'a': city_a, 'b': city_b, **values}


def store_ic_rel(city_a, city_b, values=None):
    """
    Stores a relation between the given cities and initialises the
    scores for all topics to 0. Any existing scores are overridden.

    :param city_a: City A
    :param city_b: City B
    :return: True iff stored successfully
    """
    query, params = _store_ic_rel_query(city_a, city_b, values)
    return perform_query(query, params) == []


def store_ic_rels(pairs, values=None):
    """
    Same as store_ic_rel, but for multiple city pairs

    :param pairs: A list of city tuples
    :return: True iff all pairs have been successfully stored
    """
    query_list = list()
    params_list = list()

    for i, pair in enumerate(pairs):
        if values and len(values) > i:
            query, params = _store_ic_rel_query(pair[0], pair[1], values[i])
        else:
            query, params = _store_ic_rel_query(pair[0], pair[1], None)
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

    _logger.warn('PERFORMING {} STORE_INDEX QUERIES!'.format(len(query_list)))
    return len(perform_queries(query_list, params_list)) == len(query_list)


def _store_occurrence_query(digest, cities):
    # Generates a query for storing occurrences, as a relation
    # between a city and an index. Returns a query, params tuple
    query = '''
        MATCH (i:Index {{ digest: $digest }})
        MATCH (a:City) WHERE a.name IN [ {0} ]
        MERGE (a)-[:{1}]->(i)
    '''.format(', '.join('"{}"'.format(c) for c in cities), OCCURS_IN)
    return query, {'digest': digest}


def store_occurrence(digest, cities):
    """
    Creates a relation between the given index and cities

    :param digest: The unique identifier of the index
    :param cities: The names of the cities
    :return: True iff stored successfully
    """
    return perform_query(*_store_occurrence_query(digest, cities)) == []


def store_occurrences(digests, occurrences):
    """
    Same as store_occurrence but for multple indices/occurrences.

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
        probabilities = DEFAULT_CAT_DICT_NO_OTHER

    query = '''
        MATCH (i:Index {{ digest: $digest }})
        SET {}
    '''.format(','.join('i.{}={}'.format(k, v) for k, v in probabilities.items()))
    return query, {'digest': digest}


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


def compute_ic_relations(cities=None):
    """
    Computes the relation scores per category for the given cities.
    Computation is done by simply counting the occurrences of both
    city A and city B in labelled documents. A total score is also
    calculated.

    The result set is a list of dictionaries, containing:

    `city_a`: The name of city A
    `city_b': The name of city B
    `category`: The name of the category
    `score`: The score computed for the category

    :param cities: Optional. A list of cities to compute the relations for.
    If no cities are provided, relations are computed for all cities.
    :return: A list of dictionaries of the format given above.
    """
    query = '''
        UNWIND $cities as city_a
        MATCH (:City {{ name: city_a }})-[:{0}]->
            (i:Index)<-[:{0}]-(b:City)
        WHERE b.name <> city_a
        WITH DISTINCT city_a, b, LABELS(i) as labels,
            COUNT(i) AS labelCount
        UNWIND labels AS category
        RETURN city_a, b.name AS city_b, category, SUM(labelCount) AS score
    '''.format(OCCURS_IN)

    if not cities:
        cities = city_names()

    result = list()
    for rec in perform_query(query, cities=cities, access_mode='read'):
        result.append({
            'city_a': rec['city_a'],
            'city_b': rec['city_b'],
            'category': rec['category'],
            'score': rec['score']
        })

    return result


def compute_all_ic_rels_with_threshold(threshold):
    """
    Computes all intercity relations for documents classified with higher probability
    than the given threshold.

    :param threshold: The minimum probability
    :result: A list of dictionaries with city_a, city_b, category and score fields.
    """
    query = '''
        UNWIND [{0}] AS category
        MATCH (a:City)-[:{1}]->(i:Index)<-[:{1}]-(b:City)
        WHERE ID(a) < ID(b) AND a.name <> b.name AND i[category] >= {2}
        MATCH (a)-[r:{3}]->(b)
        WITH a.name AS city_a, a.population AS pop_a, b.name AS city_b,
            b.population AS pop_b, r.total AS total, COUNT(i) AS count, category,
            2 * 6371 * asin(sqrt(haversin(radians(a.latitude - b.latitude)) +
            cos(radians(a.latitude)) * cos(radians(b.latitude)) *
            haversin(radians(a.longitude - b.longitude)))) AS dist
        RETURN city_a, pop_a, city_b, pop_b, dist, total, category, SUM(count) AS score
    '''.format(','.join('"{}"'.format(c) for c in CAT_NO_OTHER), OCCURS_IN, threshold, RELATES_TO)

    return perform_query(query, [], access_mode='read')


def _get_ic_rel_query(city_a, city_b):
    # Generates a query for retrieving intercity relation statistics
    # Returns a query, params tuple
    query = '''
        MATCH (a:City {{name: $city_a}})-[r:{0}]-(b:City {{name: $city_b}})
        RETURN a.name AS city_a, b.name AS city_b, properties(r) AS relation
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
    result = perform_query(*_get_ic_rel_query(city_a, city_b),
                           access_mode='read')
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
            for r in perform_queries(query_list, params_list,
                                     access_mode='read')]


def get_all_ic_rels():
    """
    Utility function to get all intercity relations.
    Generates a triangular matrix of all cities and retrieves the scores
    per pair.

    :return: A list of dictionaries, containing the scores per city pair
    """
    query = '''
        MATCH (c:City)-[r:RELATES_TO]->(c2:City)
        WHERE ID(c) < ID(c2) AND c.name <> c2.name
        RETURN c.name AS city_a, c.population AS pop_a, c2.name AS city_b,
            c2.population AS pop_b, properties(r) AS relation, 2 * 6371 *
                asin(sqrt(haversin(radians(c.latitude - c2.latitude)) +
                cos(radians(c.latitude)) * cos(radians(c2.latitude)) *
                haversin(radians(c.longitude - c2.longitude)))) AS dist
    '''
    result = perform_query(query, [], access_mode='read')
    ic_rels = list()
    for i, row in enumerate(result):
        relation = {k: v for k, v in row['relation'].items() if k != 'index'}
        relation['city_a'] = row['city_a']
        relation['city_b'] = row['city_b']
        relation['pop_a'] = row['pop_a']
        relation['pop_b'] = row['pop_b']
        relation['dist'] = row['dist']
        ic_rels.append(relation)
    return ic_rels


def _get_index_probabilities_query(digest):
    # Generates a query for retrieving index probabilities
    # Returns a query, params tuple
    query = '''
        MATCH (i:Index {{ digest: $digest }})
        RETURN {}
    '''.format(', '.join('i.{0} AS {0}'.format(p) for p in CAT_NO_OTHER))
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
    result = perform_query(*_get_index_probabilities_query(digest),
                           access_mode='read')
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
            for r in perform_queries(query_list, params_list,
                                     access_mode='read')]


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
    result = perform_query(*_get_index_topics_query(digest),
                           access_mode='read')
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
            for r in perform_queries(query_list, params_list,
                                     access_mode='read')]


def get_related_documents(city_a, city_b):
    """
    Retrieves a list of Common Crawl documents in which
    both city_a and city_b occur, as well as the categories these
    documents are classified as.

    :param city_a: Name of city A
    :param city_b: Name of city B
    :return: A list of dictionaries containing digest and categories.
    """
    query = '''
        MATCH (:City {{ name: $city_a }})-[:{0}]->
            (i:Index)<-[:{0}]-(:City {{ name: $city_b }})
        RETURN i.digest AS digest, labels(i) AS categories,
            properties(i) AS probabilities
    '''.format(OCCURS_IN)

    results = []
    for r in perform_query(query, {'city_a': city_a, 'city_b': city_b}):
        r['categories'].remove('Index')
        categories = {cat.lower(): r['probabilities'][cat.lower()]
                      for cat in r['categories']}
        results.append({
            'digest': r['digest'],
            'categories': categories
        })
    return results


def get_index(digest):
    """
    Returns the index as dictionary. Contains filename,
    content length and offset.
    :param digest: The unique identifier of the index
    :return: The index dictionary
    """
    query = '''
        MATCH (i:Index) WHERE i.digest = $digest
        RETURN i.filename AS filename, i.offset AS offset,
            i.length AS length
    '''
    return {**perform_query(query, {'digest': digest})[0]}


def _get_cities():
    # Returns a list of Neo4j City objects. Tries to reuse them
    # save database hits
    global _cities

    if not _cities:
        _cities = [c for c in perform_query('MATCH (a:City) RETURN a',
                                            access_mode='read')]

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
