import time

import pytest

import config

from urbansearch.utils import db_utils

OCCURS_IN = config.get('neo4j', 'occurs_in_name')
RELATES_TO = config.get('neo4j', 'relates_to_name')

if not ('TEST' in OCCURS_IN and 'TEST' in RELATES_TO):
    raise ValueError('Not adjusting production DB! {} {}'.format(RELATES_TO,
                                                                 OCCURS_IN))


@pytest.fixture
def clean_neo4j_index_and_rel(request):
    # Cleans all created relations to index named 'test*.gz'
    def clean():
        db_utils.perform_query('''
            MATCH (:City)-[r:{}]->(n:Index)
            WHERE n.filename STARTS WITH 'test'
            DELETE r, n'''.format(OCCURS_IN))

    request.addfinalizer(clean)


@pytest.fixture
def clean_neo4j_index(request):
    # Cleans all created relations to index named 'test*.gz'
    def clean():
        db_utils.perform_query('''
            MATCH (n:Index)
            WHERE n.filename STARTS WITH 'test'
            DELETE n''')

    request.addfinalizer(clean)


@pytest.fixture
def clean_neo4j_ic_rel(request):
    # Cleans all created relations labeled RELATES_TO
    def clean_ic_rel():
        db_utils.perform_query('''
            MATCH (:City)-[r:{}]->(:City)
            DELETE r'''.format(RELATES_TO), None)

    request.addfinalizer(clean_ic_rel)


def _create_test_index(digest='unique_string'):
    index = {'digest': digest, 'filename': 'test.gz', 'length': 10, 'offset': 12}
    assert db_utils.store_index(index)
    return index['digest']


def test_city_names():
    actual = db_utils.city_names()
    expected = ['Amsterdam', 'Rotterdam', 'Den Haag', 'Appingedam']
    assert actual == expected


def test_city_population():
    actual = db_utils.city_population('Amsterdam')
    expected = 697835
    assert actual == expected


def test_city_distance_diff():
    small_dist = db_utils.city_distance('Den Haag', 'Rotterdam')
    large_dist = db_utils.city_distance('Appingedam', 'Rotterdam')
    assert small_dist < large_dist


def test_city_distance_eq():
    a_to_b = db_utils.city_distance('Den Haag', 'Rotterdam')
    b_to_a = db_utils.city_distance('Rotterdam', 'Den Haag')
    assert a_to_b == b_to_a


def test_city_haversine_distance_diff():
    small_dist = db_utils.city_haversine_distance('Den Haag', 'Rotterdam')
    large_dist = db_utils.city_haversine_distance('Amsterdam', 'Rotterdam')
    assert small_dist < large_dist


def test_city_haversine_distance_eq():
    a_to_b = db_utils.city_haversine_distance('Den Haag', 'Rotterdam')
    b_to_a = db_utils.city_haversine_distance('Rotterdam', 'Den Haag')
    assert a_to_b == b_to_a


def test_city_haversine_distance_num():
    dist = db_utils.city_haversine_distance('Rotterdam', 'Amsterdam')
    assert 55 < dist < 60


def test_invalid_query():
    assert db_utils.perform_query('MATCH (n:City)') is None


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_single_index():
    index = {'digest': 'unique_string', 'filename': 'test.gz',
             'length': 10, 'offset': 12}
    assert db_utils.store_index(index)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_multi_index():
    indices = [
            {'digest': 'unique_string', 'filename': 'test.gz',
             'length': 10, 'offset': 12},
            {'digest': 'unique_string2', 'filename': 'test2.gz',
             'length': 11, 'offset': 13}
    ]
    assert db_utils.store_indices(indices)


@pytest.mark.usefixtures('clean_neo4j_index_and_rel')
def test_store_single_occurrence():
    digest = _create_test_index()
    city = 'Amsterdam'
    assert db_utils.store_occurrence(digest, [city])


@pytest.mark.usefixtures('clean_neo4j_index_and_rel')
def test_store_multi_occurrence():
    indices = [
            {'digest': 'unique_string', 'filename': 'test.gz',
             'length': 10, 'offset': 12},
            {'digest': 'unique_string2', 'filename': 'test2.gz',
             'length': 11, 'offset': 13}
    ]
    db_utils.store_indices(indices)
    digests = ['unique_string', 'unique_string2']
    occurrences = [['Amsterdam', 'Rotterdam'], ['Appingedam']]
    assert db_utils.store_occurrences(digests, occurrences)


@pytest.mark.usefixtures('clean_neo4j_ic_rel')
def test_store_intercity_relation():
    assert db_utils.store_ic_rel('Amsterdam', 'Rotterdam')


def test_get_intercity_relation_none():
    assert not db_utils.get_ic_rel('Rotterdam', 'Amsterdam')


@pytest.mark.usefixtures('clean_neo4j_ic_rel')
def test_get_intercity_relation():
    expected = {
        'commuting': 0,
        'shopping': 0,
        'leisure': 0,
        'residential_mobility': 0,
        'education': 0,
        'collaboration': 0,
        'transportation': 0,
        'other': 0,
        'total': 0
    }
    db_utils.store_ic_rel('Rotterdam', 'Amsterdam')
    assert db_utils.get_ic_rel('Rotterdam', 'Amsterdam') == expected


@pytest.mark.usefixtures('clean_neo4j_ic_rel')
def test_get_intercity_relation_multi():
    d = {
        'commuting': 0,
        'shopping': 0,
        'leisure': 0,
        'residential_mobility': 0,
        'education': 0,
        'collaboration': 0,
        'transportation': 0,
        'other': 0,
        'total': 0
    }
    expected = [d, d]
    db_utils.store_ic_rels([('Rotterdam', 'Amsterdam'),
                                ('Den Haag', 'Appingedam')])
    assert db_utils.get_ic_rels([('Rotterdam', 'Amsterdam'),
                                 ('Den Haag', 'Appingedam')]) == expected


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_index_topics_single():
    index = _create_test_index()
    topics = ['economy']
    assert db_utils.store_index_topics(index, topics)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_index_topics_multi():
    index = _create_test_index()
    topics = ['economy', 'commuting']
    assert db_utils.store_index_topics(index, topics)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_index_topics_empty():
    index = _create_test_index()
    topics = []
    assert not db_utils.store_index_topics(index, topics)
    topics = None
    assert not db_utils.store_index_topics(index, topics)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_indices_topics():
    indices = [_create_test_index(), _create_test_index('test2.gz')]
    topics = [['Economy', 'Trade'], []]
    assert db_utils.store_indices_topics(indices, topics)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_get_index_probabilities():
    index = _create_test_index()
    db_utils.store_index_probabilities()
    expected = {
        'commuting': 0,
        'shopping': 0,
        'leisure': 0,
        'residential_mobility': 0,
        'education': 0,
        'collaboration': 0,
        'transportation': 0,
        'other': 0
    }
    assert db_utils.get_index_probabilities(index) == expected


@pytest.mark.usefixtures('clean_neo4j_index')
def test_get_index_probabilities():
    indices = [_create_test_index(), _create_test_index('test2.gz')]
    db_utils.store_indices_probabilities(indices, [None, None])
    probabilities = {
        'commuting': 0,
        'shopping': 0,
        'leisure': 0,
        'residential_mobility': 0,
        'education': 0,
        'collaboration': 0,
        'transportation': 0,
        'other': 0
    }
    expected = [probabilities, probabilities]
    assert db_utils.get_indices_probabilities(indices) == expected


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_index_probabilities_default():
    index = _create_test_index()
    assert db_utils.store_index_probabilities(index, None)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_index_probabilities_full():
    digest = _create_test_index()
    probabilities = {
        'commuting': 0.5,
        'shopping': 0.13,
        'leisure': 0.12,
        'residential_mobility': 0.11,
        'education': 0.15,
        'collaboration': 0.16,
        'transportation': 0.17,
        'other': 0.19
    }
    assert db_utils.store_index_probabilities(digest, probabilities)
    assert db_utils.get_index_probabilities(digest) == probabilities


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_index_probabilities_with_update():
    index = _create_test_index()
    probabilities = {
        'commuting': 0.5,
        'shopping': 0.13,
        'leisure': 0.12,
        'residential_mobility': 0.11
    }
    update = {'commuting': 0.6}
    expected = {
        'commuting': 0.6,
        'shopping': 0.13,
        'leisure': 0.12,
        'residential_mobility': 0.11,
        'education': 0,
        'collaboration': 0,
        'transportation': 0,
        'other': 0
    }
    assert db_utils.store_index_probabilities(index, probabilities)
    assert db_utils.store_index_probabilities(index, update)
    assert db_utils.get_index_probabilities(index) == expected


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_indices_probabilities():
    indices = [_create_test_index(), _create_test_index('test2.gz')]
    values = {
        'commuting': 0.6,
        'shopping': 0.13,
        'leisure': 0.12,
        'residential_mobility': 0.11,
        'education': 0,
        'collaboration': 0,
        'transportation': 0,
        'other': 0
    }
    expected = [values, values]
    assert db_utils.store_indices_probabilities(indices, expected)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_get_index_topics():
    index = _create_test_index()
    db_utils.store_index_topics(index, ['Economy'])
    assert db_utils.get_index_topics(index) == ['Economy']


@pytest.mark.usefixtures('clean_neo4j_index')
def test_get_indices_topics():
    indices = [_create_test_index(), _create_test_index('test2.gz')]
    db_utils.store_indices_topics(indices, [['Economy'], []])
    assert db_utils.get_indices_topics(indices) == [['Economy'], []]
