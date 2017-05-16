import os
import itertools
import logging
from json.decoder import JSONDecodeError

from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence

logger = logging.getLogger(__name__)


class IndicesSelector(object):

    def __init__(self):
        self.page_downloader = gathering.PageDownloader()
        self.occurrence_checker = cooccurrence.CoOccurrenceChecker()

    def relevant_indices_from_dir(self, directory):
        """ Check all files in a directory and parse indices in the files
        in the directory.

        :directory: Path to the directory
        :returns: TODO
        """
        relevant_indices = [self.relevant_indices_from_file(_file.path)
                            for _file in os.scandir(directory)
                            if _file.is_file()]
        return list(itertools.chain.from_iterable(relevant_indices))

    def relevant_indices_from_file(self, filename):
        """TODO: Docstring for function.

        :arg1: TODO
        :returns: TODO

        """
        pd = self.page_downloader
        occ = self.occurrence_checker

        try:
            if filename.endswith(".gz"):
                pd.indices_from_gz_file(filename)
            else:
                pd.indices_from_file(filename)
        except JSONDecodeError:
            logger.error("File %s doesn't contain correct indices", filename)

        # Store all relevant indices in a list, using cooccurrence check
        relevant_indices = [index for index in pd.indices
                            if occ.check(pd.index_to_txt(index))]

        return relevant_indices


ind_sel = IndicesSelector()
relevant = ind_sel.relevant_indices_from_dir('/home/gijs/BEP/UrbanSearch/tests/resources/indices_dir/')
print(len(relevant))
test1 = (ind_sel.relevant_indices_from_file('/home/gijs/BEP/UrbanSearch/tests/resources/indices_dir/domain-nl-0000.gz'))
test2 = (ind_sel.relevant_indices_from_file('/home/gijs/BEP/UrbanSearch/tests/resources/indices_dir/indices2.txt'))
print(test1)
print(test2)
print(len(list(itertools.chain.from_iterable([test1, test2]))))

