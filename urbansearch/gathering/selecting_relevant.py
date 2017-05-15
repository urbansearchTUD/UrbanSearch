import os
import itertools

from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence


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
        relevant_indices = [self.relevant_indices_from_file(filename)
                            for filename in os.scandir(directory)]
        return list(itertools.chain.from_iterable(relevant_indices))

    def relevant_indices_from_file(self, filename):
        """TODO: Docstring for function.

        :arg1: TODO
        :returns: TODO

        """
        pd = self.page_downloader
        occ = self.occurrence_checker

        if filename.endswith(".gz"):
            pd.indices_from_gz_file(filename)
        else:
            pd.indices_from_file(filename)

        # Store all relevant indices in a list, using cooccurrence check
        relevant_indices = [index for index in pd.indices
                            if occ.check(pd.index_to_txt(index))]

        return relevant_indices


pd = gathering.PageDownloader()
pd.indices_from_gz_file('/home/gijs/BEP/domain-nl-0000.gz')
print(len(pd.indices))
oc_chkr = cooccurrence.CoOccurrenceChecker()
ind_sel = IndicesSelector()
ind_sel.relevant_indices_from_file('/home/gijs/BEP/domain-nl-0000.gz')

i = 0
for index in pd.indices:
    txt = pd.index_to_txt(index)
    occ = oc_chkr.check(txt)
    if occ:
        print(occ)
    i+=1
    print(i)
