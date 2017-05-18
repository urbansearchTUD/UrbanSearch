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
# NOTE: when running these tests locally, some will fail, since they are run against the production
# database. Travis has it's own database, containing only what is mentioned above.

@pytest.fixture
def clean_neo4j(request):
    # Cleans all created relations to index named 'test.gz'
    def clean():
        print('Cleaning database...')
        db_utils.perform_query('MATCH ()-[r]->(n:Index {filename: "test.gz"}) DELETE r, n')
        print('Done!')

    request.addfinalizer(clean)


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


@pytest.mark.usefixtures('clean_neo4j')
def test_store_single_cooccurrence():
    index = {'filename': 'test.gz', 'length': 10, 'offset': 12}
    co_occurrences = [('Amsterdam', 'Rotterdam')]
    topics = ['economy', 'tourism']
    assert db_utils.store_index(index=index, co_occurrences=co_occurrences, topics=topics)


@pytest.mark.usefixtures('clean_neo4j')
def test_store_single_cooccurrence_no_topic():
    index = {'filename': 'test.gz', 'length': 10, 'offset': 12}
    co_occurrences = [('Amsterdam', 'Rotterdam')]
    assert db_utils.store_index(index=index, co_occurrences=co_occurrences)


@pytest.mark.usefixtures('clean_neo4j')
def test_store_multi_cooccurrence():
    index = {'filename': 'test.gz', 'length': 10, 'offset': 12}
    co_occurrences = [('Amsterdam', 'Rotterdam'), ('Amsterdam', 'Appingedam'), ('Rotterdam', 'Appingedam')]
    topics = ['economy', 'tourism']
    assert db_utils.store_index(index=index, co_occurrences=co_occurrences, topics=topics)


@pytest.mark.usefixtures('clean_neo4j')
def test_store_multi_cooccurrences_no_topic():
    index = {'filename': 'test.gz', 'length': 10, 'offset': 12}
    co_occurrences = [('Amsterdam', 'Rotterdam'), ('Amsterdam', 'Appingedam'), ('Rotterdam', 'Appingedam')]
    assert db_utils.store_index(index=index, co_occurrences=co_occurrences)
