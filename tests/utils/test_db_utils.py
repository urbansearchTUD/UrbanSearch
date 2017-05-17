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

def test_for_travis():
    assert len(db_utils.city_names()) == 3
