import ahocorasick
import collections
import itertools

from urbansearch.utils import db_utils


class CoOccurrenceChecker(object):
    def __init__(self, cities=None):
        """
        Initialises the co-occurrence checker. If a list of cities is provided, that list will be checked against.
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
        Checks the given page for city co-occurrences and returns them as a list.

        :param page: A string to be checked for city co-occurrences.
        :return: The co-occurrences as a list of tuples of city names or None.
        """
        if not isinstance(page, str):
            raise TypeError('Expected a string object but got %s' % type(page))

        # Retrieve all occurrences of cities, with overlapping occurrences (e.g. Ee and Een) removed.
        # Additionally, duplicate occurrences are removed as the result of clean is a set.
        occurrences = self._calculate_occurrences(page)

        # if the occurrence list is smaller than 2, there are no co-occurrences and the page may be discared.
        if len(occurrences) < 2:
            return None

        # Return a list of tuples, with each tuple being a co-occurrence of two cities.
        return list(itertools.combinations(occurrences, 2))

    def _calculate_occurrences(self, page):
        occurrences = self.automaton.iter(page)
        result_set = collections.OrderedDict()

        # Loop over the occurrences pairwise: (1, 2), (2, 3), (3, 4), etc.
        prev_occurrence = next(occurrences, None)
        for occurrence in occurrences:
            # If the end indices of a pair are within the length of an occurrence, there is overlap.
            if abs(occurrence[0] - prev_occurrence[0]) < len(occurrence[1]):
                longer = occurrence[1] if len(occurrence[1]) > len(prev_occurrence[1]) else prev_occurrence[1]
                result_set[longer] = None
                # Skip next to avoid processing the overlap in the next pair
                prev_occurrence = next(occurrences, None)
            # If there is no overlap, just add the city names to the result set.
            else:
                result_set[prev_occurrence[1]] = None
                prev_occurrence = occurrence

        if prev_occurrence:
            result_set[prev_occurrence[1]] = None

        return result_set.keys()
