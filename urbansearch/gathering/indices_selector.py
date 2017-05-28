import os
import itertools
import logging
from json.decoder import JSONDecodeError
from multiprocessing import Process

from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence
from urbansearch.utils import process_utils, db_utils
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

    def relevant_indices_from_file(self, filepath, to_database=False):
        """ Collect all indices from file and return files that are relevant.
        An index is relevant if it contains at least one co-occurrence of
        cities. Input file can be .gz or document containing string
        representations of json.

        :filepath: Path to the file containing indices
        :to_database: Store the indices and co-occurrences in the database
        :returns: List of relevant indices, in python JSON format

        """
        pd = self.page_downloader
        occ = self.occurrence_checker
        try:
            if filepath.endswith('.gz'):
                indices = pd._worker_indices_from_gz_file(filepath)
            else:
                indices = pd.indices_from_file(filepath)
        except JSONDecodeError:
            logger.error('File {0} doesn\'t contain correct indices'
                         .format(filepath))
            indices = None

        # Store all relevant indices in a list, using cooccurrence check
        # relevant_indices = [index for index in indices
        #                    if occ.check(pd.index_to_txt(index))]
        # Uncomment and remove lines below if progress is not interesting
        relevant_indices = []
        i = 0
        n = len(indices)
        for index in indices:
            i += 1
            if i % 10 == 0:
                logger.info("Index {0}/{1} of file {2}".format(i, n, filepath))
            co_occ = occ.check(pd.index_to_txt(index))
            if co_occ:
                relevant_indices.append(index)
                if to_database:
                    db_utils.store_index(index, co_occ, None)
        return relevant_indices

    def run_workers(self, num_workers, directory, queue, opt=False):
        """ Run workers to process indices from a directory with files
        in parallel. All parsed indices will be added to the queue.

        :num_workers: Number of workers that will run
        :directory: Path to directory containing files
        :queue: multiprocessing.Queue where the indices will be added to
        :opt: Determine optimal number of workers and ignore num_workers
        parameter
        """
        if opt:
            num_workers = process_utils.compute_num_workers()

        files = [_file.path for _file in os.scandir(directory)
                 if _file.is_file()]

        div_files = process_utils.divide_files(files, num_workers)
        workers = [Process(target=self.worker, args=(queue, div_files[i]))
                   for i in range(num_workers)]

        for worker in workers:
            worker.start()

        # Wait for processes to finish
        for worker in workers:
            worker.join()

    def worker(self, queue, files):
        """
        Worker that will parse indices from files in file list and put the
        results in a Queue. Can use plain text files containing indices or
        .gz files containing indices.

        :queue: multiprocessing.JoinableQueue to put results in
        :files: List of filepaths to files that this worker will use
        """
        for file in files:
            for index in self.relevant_indices_from_file(file):
                queue.put(index)
