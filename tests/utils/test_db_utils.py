import time

from urbansearch.utils import db_utils


# Cities available in the test database:
# Amsterdam, Rotterdam, Den Haag

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
    expected = ['Amsterdam', 'Rotterdam', 'Den Haag']
    assert actual == expected


def test_city_population():
    actual = db_utils.city_population('Amsterdam')
    expected = 697835
    assert actual == expected


def test_city_distance_diff():
    small_dist = db_utils.city_distance('Den Haag', 'Rotterdam')
    large_dist = db_utils.city_distance('Amsterdam', 'Rotterdam')
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
