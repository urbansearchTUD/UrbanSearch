import os
import itertools
import logging
from json.decoder import JSONDecodeError
from multiprocessing import Process, Manager, Value, Lock
from ctypes import c_int
import sys
import timeit
import gzip

from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence
from urbansearch.utils import process_utils, db_utils

logger = logging.getLogger(__name__)
counter = Value(c_int)  # defaults to 0
counter_lock = Lock()

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
            with counter_lock:
                counter.value += 1
            i += 1
            if i % 10 == 0:
                logger.info('Index {0}/{1} of file {2}'.format(i, n, filepath))
            if occ.check(pd.index_to_txt(index)):
                relevant_indices.append(index)
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

        # Count lines of all files
        # TODO move to process_utils
        lines = 0
        for file in files:
            if file.endswith('.gz'):
                with gzip.GzipFile(file) as gz_obj:
                    for l in gz_obj.read().decode('utf-8').split('\n'):
                        lines += 1
        
        for worker in workers:
            worker.start()

        # TODO Move to function
        start = 0
        been = False
        while counter.value < lines:
            if counter.value == 1:
                start = timeit.default_timer()
            if counter.value % 100 == 0 and not been:
                stop = timeit.default_timer()
                avg = (stop - start) / 100
                remaining = (lines - counter.value) * avg
                m, s = divmod(remaining, 60)
                h, m = divmod(m, 60)

                sys.stdout.write('Progress: {0}/{1} Left: {2} h {3} m {4} s\r'
                                 .format(counter.value, lines, h, m, s))
                sys.stdout.flush()
                start = timeit.default_timer()
                been = True
            if counter.value % 100 != 0:
                been = False

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

ind_sel = IndicesSelector()
man = Manager()
q = man.Queue()
ind_sel.run_workers(48, '/home/gijs/BEP/test/', q)
