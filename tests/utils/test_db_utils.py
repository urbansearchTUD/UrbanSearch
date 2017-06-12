import time

import pytest

from urbansearch.utils import db_utils


# Cities available in the test database:
# Amsterdam, Rotterdam, Den Haag and Appingedam

# │{"latitude":52.3702157,"name":│
# │"Amsterdam","longitude":4.8951│
# │679,"population":"697835"}    │
# ├──────────────────────────────┤
# │{"latitude":51.9244201,"name":│
# │"Rotterdam","longitude":4.4777│
# │325,"population":"549355"}    │
# ├──────────────────────────────┤
# │{"latitude":52.0704978,"name":│
# │"Den Haag","longitude":4.30069│
# │99,"population":"495010"}
#
# NOTE: when running these tests locally, some will fail, since they are run
# against the production database. Travis has it's own database, containing
# only what is mentioned above.

@pytest.fixture
def clean_neo4j_index_and_rel(request):
    # Cleans all created relations to index named 'test.gz'
    def clean():
        db_utils.perform_query('MATCH ()-[r]->(n:Index {filename: "test.gz"})'
                               'DELETE r, n')

    request.addfinalizer(clean)


@pytest.fixture
def clean_neo4j_index(request):
    # Cleans all created relations to index named 'test.gz'
    def clean():
        db_utils.perform_query('MATCH (n:Index {filename:"test.gz"}) DELETE n')

    request.addfinalizer(clean)


@pytest.fixture
def clean_neo4j_ic_rel(request):
    # Cleans all created relations labeled REL_TEST
    def clean_ic_rel():
        db_utils.perform_query('MATCH ()-[r:REL_TEST]->() DELETE r')

    request.addfinalizer(clean_ic_rel)


def _create_test_index(cooccurrences=list()):
    index = {'filename': 'test.gz', 'length': 10, 'offset': 12}
    db_utils.store_index(index, cooccurrences)
    return index['filename']


def test_caching():
    # Without cities cached
    start = time.time()
    db_utils.city_names()
    time_a = time.time() - start
    # With cities cached
    start = time.time()
    db_utils.city_names()
    time_b = time.time() - start
    assert time_a > time_b


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


@pytest.mark.usefixtures('clean_neo4j_index_and_rel')
def test_store_single_cooccurrence():
    index = {'filename': 'test.gz', 'length': 10, 'offset': 12}
    co_occurrences = [('Amsterdam', 'Rotterdam')]
    assert db_utils.store_index(index=index, co_occurrences=co_occurrences)


@pytest.mark.usefixtures('clean_neo4j_index_and_rel')
def test_store_multi_cooccurrence():
    index = {'filename': 'test.gz', 'length': 10, 'offset': 12}
    co_occurrences = [('Amsterdam', 'Rotterdam'), ('Amsterdam', 'Appingedam'),
                      ('Rotterdam', 'Appingedam')]
    assert db_utils.store_index(index=index, co_occurrences=co_occurrences)


@pytest.mark.usefixtures('clean_neo4j_ic_rel')
def test_store_intercity_relation():
    assert db_utils.store_ic_rel('Amsterdam', 'Rotterdam', rel_name='REL_TEST')


def test_get_intercity_relation_none():
    assert db_utils.get_ic_rel('Rotterdam', 'Amsterdam', rel_name='REL_TEST')\
           is None


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
        'other': 0
    }
    db_utils.store_ic_rel('Rotterdam', 'Amsterdam', rel_name='REL_TEST')
    assert db_utils.get_ic_rel('Rotterdam', 'Amsterdam',
                               rel_name='REL_TEST') == expected


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
def test_store_index_probabilities_default():
    index = _create_test_index()
    assert db_utils.store_index_probabilities(index, None)


@pytest.mark.usefixtures('clean_neo4j_index')
def test_store_index_probabilities_full():
    index = _create_test_index()
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
    assert db_utils.store_index_probabilities(index, probabilities)
    assert db_utils.get_index_probabilities(index) == probabilities


@pytest.mark.usefixtures('clean_neo4j_ic_rel')
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
def test_store_index_probabilities_invalid():
    index = _create_test_index()
    probabilities = {'invalid': 1}
    with pytest.raises(ValueError):
        db_utils.store_index_probabilities(index, probabilities)
