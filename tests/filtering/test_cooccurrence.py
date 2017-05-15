import pytest
import os
import config
from urbansearch.filtering import cooccurrence

c = cooccurrence.CoOccurrenceChecker(cities=['Amsterdam', 'Amsterdam Zuidoost', 'Den Haag', 'Rotterdam'])


def test_single_occurrence():
    assert c.check('Amsterdam') is None


def test_single_cooccurrence():
    expected = [('Amsterdam', 'Rotterdam')]
    result_set = c.check('Amsterdam and Rotterdam are Dutch cities')
    assert (result_set == expected)


def test_multi_cooccurrence():
    expected = [('Rotterdam', 'Amsterdam'), ('Rotterdam', 'Den Haag'), ('Amsterdam', 'Den Haag')]
    assert (c.check('Rotterdam, Amsterdam and Den Haag are the three largest cities of the Netherlands') == expected)


def test_first_overlap():
    assert (c.check('Amsterdam Zuid-Oost is a city') is None)


def test_last_overlap():
    expected = [('Rotterdam', 'Amsterdam Zuidoost')]
    assert (c.check('Rotterdam and Amsterdam Zuidoost are cities') == expected)


def test_overlap():
    expected = [('Rotterdam', 'Den Haag'), ('Rotterdam', 'Amsterdam'), ('Rotterdam', 'Amsterdam Zuidoost'),
                ('Den Haag', 'Amsterdam'), ('Den Haag', 'Amsterdam Zuidoost'), ('Amsterdam', 'Amsterdam Zuidoost')]
    actual = c.check('The following cities are related: Rotterdam, Den Haag, Amsterdam and Amsterdam Zuidoost.')
    assert (actual == expected)


def test_only_accept_string():
    with open(os.path.join(config.get('resources', 'test'), 'test.txt'), 'r') as f:
        with pytest.raises(TypeError):
            c.check(f)
