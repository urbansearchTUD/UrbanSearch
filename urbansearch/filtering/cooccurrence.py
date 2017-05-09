import ahocorasick
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

        self.occurrences = None

    def check(self, page):
        """
        Checks the given page for city co-occurrences and returns them as a list.

        :param page: A string to be checked for city co-occurrences.
        :return: The co-occurrences as a list of tuples of city names or None.
        """
        if not isinstance(page, str):
            raise IOError('Expected a string object but got %s' % type(page))

        # Retrieve all occurrences of cities, with overlapping occurrences (e.g. Ee and Een) removed.
        # Additionally, duplicate occurrences are removed as the result of clean is a set.
        self._clean(self.automaton.iter(page))

        # if the occurrence list is smaller than 2, there are no co-occurrences and the page may be discared.
        if len(self.occurrences) < 2:
            return None

        # Return a list of tuples, with each tuple being a co-occurrence of two cities.
        return list(itertools.combinations(self.occurrences, 2))

    def _clean(self, raw_occurrences):
        result_set = set()

        # Loop over the occurrences pairwise: (1, 2), (2, 3), (3, 4), etc.
        current = next(raw_occurrences, None)
        for occurrence in raw_occurrences:
            # If the end indices of a pair are within the length of an occurrence, there is overlap.
            if abs(current[0] - occurrence[0]) < len(current[1]):
                longer = current[1] if len(current[1]) > len(occurrence[1]) else occurrence[1]
                # On overlap, only add the longer city name to the result set (e.g. discard Ee when Een is encountered)
                result_set.add(longer)
            # If there is no overlap, just add the city name to the result set.
            else:
                result_set.add(current[1])

            current = occurrence

        self.occurrences = result_set
