import ahocorasick
import collections
import itertools
import logging

from urbansearch.utils import db_utils


logger = logging.getLogger('filtering')


class CoOccurrenceChecker(object):
    def __init__(self, cities=None):
        """
        Initialises the co-occurrence checker. If a list of cities
        is provided, that list will be checked against.
        Else, the city list is collected from Neo4j.

        :param cities: A list of cities. Defaults to None.
        """
        # Retrieve cities from Neo4j unless provided
        if not cities:
            cities = db_utils.city_names()

        # Create the automaton to be used for Aho-Corasick
        self.automaton = ahocorasick.Automaton()
        # Add all city names to the automaton
        [self.automaton.add_word(city, city) for city in cities]
        self.automaton.make_automaton()

    def check(self, page):
        """
        Checks the given page for city co-occurrences and returns
        them as a list.

        :param page: A string to be checked for city co-occurrences.
        :return: The occurrences as a list of city
        names or None.
        """
        if not isinstance(page, str):
            raise TypeError('Expected a string object but got %s' % type(page))

        # Retrieve all occurrences of cities, with overlapping
        # occurrences (e.g. Ee and Een) removed.
        # Additionally, duplicate occurrences are removed as the
        # result of clean is a set.
        occurrences = self._calculate_occurrences(page)

        # if the occurrence list is smaller than 2, there are no
        # co-occurrences and the page may be discared.
        # Also, a maximum of 25 occurrences is allowed. See the report
        # for justification
        if not (2 < len(occurrences) < 25):
            return None

        return occurrences

    def _calculate_occurrences(self, page):
        names = self.automaton.iter(page)
        result_set = collections.OrderedDict()

        prev_end, prev_name = next(names, (None, None))
        for end, name in names:
            # Skip words that contain city names (e.g. Amsterdammers)
            if page[prev_end + 1] in 'abcdefghijklmnopqrstuvwxyz':
                prev_end, prev_name = end, name
            # Skip cities if they are part of another city (e.g. Amsterdam
            # when Amsterdam Zuidoost occurs)
            elif abs(end - prev_end) < len(name):
                longer = name if len(name) > len(prev_name) else prev_name
                result_set[longer] = None
                prev_end, prev_name = next(names, (None, None))
            else:
                result_set[prev_name] = None
                prev_end, prev_name = end, name

        # Add the last occurrence
        if prev_name:
            result_set[prev_name] = None

        return list(result_set.keys())
