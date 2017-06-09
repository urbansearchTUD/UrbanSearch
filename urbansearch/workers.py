import os
import logging
from queue import Empty
from multiprocessing import Process, Event
from ast import literal_eval

from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence
from urbansearch.clustering import classifytext, text_preprocessor
from urbansearch.utils import db_utils
producers_done = Event()
file_producers_done = Event()

LOGGER = logging.getLogger(__name__)


class Workers(object):

    """
    Worker class. Contains workers and functions to run workers.
    """

    def __init__(self):
        self.pd = gathering.PageDownloader()
        self.ct = classifytext.ClassifyText()
        self.co = cooccurrence.CoOccurrenceChecker()
        self.prepr = text_preprocessor.PreProcessor()

    def run_classifying_workers(self, no_of_workers, queue, join=True,
                                to_db=False, pre_downloaded=False):
        """ Run workers to classify indices consumed from the queue in
        parallel. Workers will only terminate if producers are done, which can
        be signaled setting the producer_done event.

        :no_of_workers: Number of workers that will run
        :queue: multiprocessing.Queue where the indices will be added to
        :join: Wait for workers to be done and join. Default is True.
        parameter
        """
        func = self.classifying_worker
        if pre_downloaded:
            func = self.classifying_from_files_worker

        workers = [Process(target=func, args=(queue, to_db))
                   for i in range(no_of_workers)]

        for worker in workers:
            worker.start()

        LOGGER.info("Classifying workers started")

        if join:
            # Wait for processes to finish
            for worker in workers:
                worker.join()
        else:
            return workers

    def classifying_worker(self, queue, to_db):
        """ Classifying worker that classifies relevant indices from a queue.
        Can output to database. Worker stops if queue is Empty and received
        signal that the producers that fill the queue are done. See function
        set_producers_done()

        :queue: Queue containing indices
        :to_db: Output index and category to database
        """
        global producers_done

        while not queue.empty() or not producers_done.is_set():
            try:
                index, co_occ = queue.get_nowait()
                txt = self.pd.index_to_txt(index)
                category = self.ct.predict(txt, self.prepr.pre_process)
                prob = self.ct.probability_per_category(txt,
                                                        self.prepr.pre_process)
                if to_db:
                    self._store_in_db(index, prob, co_occ, pre_downloaded=False)
                    LOGGER.debug("Inserting {0} for {1} and index: {2}"
                                 .format(prob, co_occ, index))
                LOGGER.info("Category: {0} for index {1}".format(category,
                                                                 index))
                LOGGER.info("Probabilities: {0} for index {1}".format(prob,
                                                                      index))
            except Empty:
                pass

    def classifying_from_files_worker(self, queue, to_db=False):
        """ Classifying worker that classifies plain text files of relevant
        indices from a directory. Can output to database.
        Worker stops if queue is Empty and received signal that the file
        reading producers that fill the queue are done. See function
        set_file_producers_done()

        :queue: Queue containing indices and text
        :to_db: Output index and category to database
        """
        global file_producers_done

        while not queue.empty() or not file_producers_done.is_set():
            try:
                index, txt = queue.get_nowait()
                co_occ = self.co.check(txt)
                prob = self.ct.probability_per_category(txt,
                                                        self.prepr.pre_process)
                LOGGER.debug("Parsed index: {0} || {1}".format(index, prob))

                if to_db:
                    self._store_in_db(index, prob, co_occ, pre_downloaded=True)
            except Empty:
                pass

    def _store_in_db(self, index, probabilities, co_occ, pre_downloaded=False):
        # If files are already downloaded, but not inserted in the db yet
        if pre_downloaded:
            db_utils.store_index(index, co_occ)
        self._store_ic_rel(co_occ)
        db_utils.store_index_probabilities(index, probabilities)

    def run_read_files_worker(self, directory, queue, join=True):
        """ Run a worker to read all pre-downloaded files from a directory,
        which were downloaded using TextDownloader module. Output index, text
        tuple to the queue.

        :directory: Path to directory containing text files in correct format
        :queue: Queue to add the tuples to
        :join: Wait for worker to finish in this function or return the Process
        :return: Return the multiprocessing.Process if join = False

        """
        # 1 worker is probably best as it's way faster than classifying
        worker = [Process(target=self.read_files_worker, args=(directory,
                                                               queue))]

        LOGGER.info("File reading worker started")

        worker[0].start()

        if join:
            # Wait for processes to finish
            worker.join()
        else:
            return worker

    def read_files_worker(self, directory, queue):
        """ Read all files in a directory and output to the queue. First line
        of every file should contain the index. Worker separates first line
        and parses to dict. Tuple of index and text is added to queue.

        :directory: Source directory containing files
        :queue: Queue to add the tuples to
        """
        for file in os.scandir(directory):
            if file.is_file():
                with open(file.path, 'r') as f:
                    text = f.readlines()
                    index = literal_eval(text.pop(0).strip())
                    queue.put_nowait((index, '\n'.join(text)))

    def _store_ic_rel(self, co_occ):
        # Store all co-occurences as relations in database using db_utils
        for city_a, city_b in co_occ:
            if db_utils.store_ic_rel(city_a, city_b):
                pass
            else:
                LOGGER.error("Database did not store IC_REL {0}-{1}"
                             .format(city_a, city_b))

    def set_producers_done(self):
        """ Set the signal that producers are done.

        """
        global producers_done
        producers_done.set()

    def clear_producers_done(self):
        """ Clear the signal that producers are done.

        """
        global producers_done
        producers_done.clear()

    def set_file_producers_done(self):
        """ Set the signal that producers are done.

        """
        global file_producers_done
        file_producers_done.set()

    def clear_file_producers_done(self):
        """ Clear the signal that producers are done.

        """
        global file_producers_done
        file_producers_done.clear()
