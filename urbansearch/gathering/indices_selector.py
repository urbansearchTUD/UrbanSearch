import os
import itertools
import logging
from json.decoder import JSONDecodeError
from multiprocessing import Process

from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence
from urbansearch.utils import process_utils, db_utils, progress_utils
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

    def relevant_indices_from_file(self, filepath, to_database=False,
                                   worker=False, progress=False):
        """ Collect all indices from file and return files that are relevant.
        An index is relevant if it contains at least one co-occurrence of
        cities. Input file can be .gz or document containing string
        representations of json.

        :filepath: Path to the file containing indices
        :to_database: Store the indices and co-occurrences in the database
        :returns: List of relevant indices, in python JSON format

        """
        pd = self.page_downloader
        try:
            if filepath.endswith('.gz'):
                indices = pd._worker_indices_from_gz_file(filepath)
            else:
                indices = pd.indices_from_file(filepath)
        except JSONDecodeError:
            logger.error('File {0} doesn\'t contain correct indices'
                         .format(filepath))
            indices = None

        return self._relevant_indices(indices, to_database, worker, progress)

    def _relevant_indices(self, indices, to_database, worker, progress=False):
        pd = self.page_downloader
        occ = self.occurrence_checker
        relevant_indices = []

        for index in indices:
            if progress:
                with progress_utils.ind_counter_lock:
                    progress_utils.ind_counter.value += 1
            try:
                co_occ = occ.check(pd.index_to_txt(index))
            except (UnicodeDecodeError, TypeError) as e:
                logger.warning("Could not convert index to txt: {0}".format(e))

            if co_occ:
                if to_database:
                    db_utils.store_index(index, co_occ)
                # If called from workers, return tuple to add to queue
                if worker:
                    relevant_indices.append((index, co_occ))
                else:
                    relevant_indices.append(index)

        return relevant_indices

    def run_workers(self, num_workers, directory, queue, **kwargs):
        """ Run workers to process indices from a directory with files
        in parallel. All parsed indices will be added to the queue.

        :num_workers: Number of workers that will run
        :directory: Path to directory containing files
        :queue: multiprocessing.Queue where the indices will be added to
        :opt: Determine optimal number of workers and ignore num_workers
        parameter
        """
        if kwargs.get('opt', False):
            num_workers = process_utils.compute_num_workers()

        files = [_file.path for _file in os.scandir(directory)
                 if _file.is_file()]

        div_files = process_utils.divide_files(files, num_workers)
        workers = [Process(target=self.worker, args=(queue, div_files[i],
                                                     kwargs.get('progress',
                                                                False)))
                   for i in range(num_workers)]

        for worker in workers:
            worker.start()

        if kwargs.get('join', True):
            # Wait for processes to finish
            for worker in workers:
                worker.join()
        else:
            return workers

    def worker(self, queue, files, progress=False):
        """
        Worker that will parse indices from files in file list and put the
        results in a Queue. Can use plain text files containing indices or
        .gz files containing indices.

        :queue: multiprocessing.JoinableQueue to put results in
        :files: List of filepaths to files that this worker will use
        """
        for file in files:
            for index in self.relevant_indices_from_file(file, worker=True,
                                                         progress=progress):
                queue.put(index)
