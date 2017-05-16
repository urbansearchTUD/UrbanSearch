import os
import itertools
import logging
from json.decoder import JSONDecodeError

from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence

logger = logging.getLogger(__name__)


class IndicesSelector(object):

    def __init__(self, cities=None):
        self.page_downloader = gathering.PageDownloader()
        self.occurrence_checker = cooccurrence.CoOccurrenceChecker(cities)

    def relevant_indices_from_dir(self, directory):
        """ Check all files in a directory and parse indices in the files
        in the directory.

        :directory: Path to the directory
        :returns: List of relevant indices, in python json format
        """
        relevant_indices = [self.relevant_indices_from_file(_file.path)
                            for _file in os.scandir(directory)
                            if _file.is_file()]
        return list(itertools.chain.from_iterable(relevant_indices))

    def relevant_indices_from_file(self, filepath):
        """ Collect all indices from file and return files that are relevant.
        An index is relevant if it contains at least one co-occurrence of
        cities. Input file can be .gz or document containing string
        representations of json.

        :filepath: Path to the file containing indices
        :returns: List of relevant indices, in python JSON format

        """
        pd = self.page_downloader
        occ = self.occurrence_checker

        try:
            if filepath.endswith(".gz"):
                indices = pd.indices_from_gz_file(filepath)
            else:
                indices = pd.indices_from_file(filepath)
        except JSONDecodeError:
            logger.error("File %s doesn't contain correct indices", filepath)

        # Store all relevant indices in a list, using cooccurrence check
        relevant_indices = [index for index in indices
                            if occ.check(pd.index_to_txt(index))]

        return relevant_indices
