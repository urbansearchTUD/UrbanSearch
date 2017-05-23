from urbansearch.utils import process_utils


def test_divide_empty_files():
    assert process_utils.divide_files([], 0) is None


def test_divide_empty_files_2():
    assert process_utils.divide_files([], 2) is None


def test_divide_files_():
    actual = process_utils.divide_files(['a', 'b', 'c', 'd'], 2)
    assert actual[0][0] == 'a'
    assert actual[1][0] == 'c'
    assert len(actual) == 2


def test_divide_files_odd():
    actual = process_utils.divide_files(['a', 'b', 'c', 'd', 'e'], 2)
    assert actual[0][0] == 'a'
    assert actual[1][2] == 'e'
    assert len(actual) == 2
