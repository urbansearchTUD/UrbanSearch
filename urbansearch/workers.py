import os
import logging
from queue import Empty
from multiprocessing import Process, Event
from ast import literal_eval

import config
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
        self.commit = config.get('neo4j', 'commit_threshold')

    def run_classifying_workers(self, no_of_workers, queue, threshold,
                                **kwargs):
        """ Run workers to classify indices consumed from the queue in
        parallel. Workers will only terminate if producers are done, which can
        be signaled setting the producer_done event.

        :no_of_workers: Number of workers that will run
        :queue: multiprocessing.Queue where the indices will be added to
        :threshold: Threshold for categories, if probability of category is
        higher than threshold the label is added.
        :join: Wait for workers to be done and join. Default is True.
        parameter
        """
        func = self.classifying_worker
        if kwargs.get('pre_downloaded', False):
            func = self.classifying_from_files_worker

        workers = [Process(target=func, args=(queue, threshold,
                                              kwargs.get('to_db', False)))
                   for i in range(no_of_workers)]

        for worker in workers:
            worker.start()

        LOGGER.info("Classifying workers started")

        if kwargs.get('join', True):
            # Wait for processes to finish
            for worker in workers:
                worker.join()
        else:
            return workers

    def classifying_worker(self, queue, threshold, to_db):
        """ Classifying worker that classifies relevant indices from a queue.
        Can output to database. Worker stops if queue is Empty and received
        signal that the producers that fill the queue are done. See function
        set_producers_done()

        :queue: Queue containing indices
        :to_db: Output index and category to database
        """
        global producers_done

        indices = list()
        digests = list()
        occurrences = list()
        probabilities = list()
        topics_list = list()

        while not queue.empty() or not producers_done.is_set():
            try:
                index, co_occ = queue.get(block=True, timeout=5)
                txt = self.pd.index_to_txt(index)
                prob = self.ct.probability_per_category(txt,
                                                        self.prepr.pre_process)
                topics = self.ct.categories_above_threshold(prob, threshold)

                if to_db:
                    self._store_indices_db(index, indices)
                    digests.append(index.get('digest', None))

                    self._store_info_db(digests, co_occ, occurrences,
                                        db_utils.store_occurrences)
                    self._store_info_db(digests, prob, probabilities,
                                        db_utils.store_indices_probabilities)
                    self._store_info_db(digests, topics, topics_list,
                                        db_utils.store_indices_topics)

                    if len(digests) >= self.commit:
                        digests.clear()
            except Empty:
                pass
        if to_db:
            LOGGER.info('Storing classification')
            self._final_store_db(indices, digests, occurrences, probabilities,
                                 topics_list)
            LOGGER.info('Done storing classification')

    def classifying_from_files_worker(self, queue, threshold, to_db=False):
        """ Classifying worker that classifies plain text files of relevant
        indices from a directory. Can output to database.
        Worker stops if queue is Empty and received signal that the file
        reading producers that fill the queue are done. See function
        set_file_producers_done()

        :queue: Queue containing indices and text
        :to_db: Output index and category to database
        """
        global file_producers_done

        indices = list()
        digests = list()
        occurrences = list()
        probabilities = list()
        topics_list = list()

        while not queue.empty() or not file_producers_done.is_set():
            try:
                index, txt = queue.get(block=True, timeout=5)
                co_occ = self.co.check(txt)
                if not co_occ:
                    continue
                prob = self.ct.probability_per_category(txt,
                                                        self.prepr.pre_process)
                topics = self.ct.categories_above_threshold(prob, threshold)
                if to_db:
                    self._store_indices_db(index, indices)
                    digests.append(index.get('digest', None))

                    self._store_info_db(digests, (co_occ, occurrences),
                                        db_utils.store_occurrences)
                    self._store_info_db(digests, (prob, probabilities),
                                        db_utils.store_indices_probabilities)
                    self._store_info_db(digests, (topics, topics_list),
                                        db_utils.store_indices_topics)

                    if len(digests) >= self.commit:
                        digests.clear()
            except Empty:
                pass
        if to_db:
            data_lists = [indices, digests, occurrences, probabilities,
                          topics_list]
            self._final_store_db(data_lists)

    def _store_indices_db(self, index, indices, final=False):
        if index and indices is not None:
            indices.append(index)

        if index is None and final:
            db_utils.store_indices(indices)

        if len(indices) >= self.commit:
            if not db_utils.store_indices(indices):
                LOGGER.error("Could not store indices in DB, query failed")
            indices.clear()

    def _store_info_db(self, digests, items, util_func, final=False):
        # Store in database using supplied item, list and function
        itm, itm_list = items
        if not itm and not itm_list:
            return
        elif itm is None and final:
            util_func(digests, itm_list)
            return

        itm_list.append(itm)

        # Accumulate data to speed up db insertion
        if len(itm_list) >= self.commit:
            LOGGER.info('Storing {}...'.format(util_func.__name__))
            if not util_func(digests, itm_list):
                LOGGER.error("Could not store list in DB, query failed")
            LOGGER.info('Done storingi {}.'.format(util_func.__name__))
            itm_list.clear()

    def _final_store_db(self, data_lists):
        indices = data_lists[0]
        digests = data_lists[1]
        occurrences = data_lists[2]
        probabilities = data_lists[3]
        topics_list = data_lists[4]

        # When done with queue but not above threshold still push to DB
        LOGGER.info('Final storing')
        self._store_indices_db(None, indices, final=True)
        LOGGER.info('Final storing indices done')
        self._store_info_db(digests, (None, occurrences),
                            db_utils.store_occurrences, final=True)
        LOGGER.info('Final storing occurrences done')
        self._store_info_db(digests, (None, probabilities),
                            db_utils.store_indices_probabilities, final=True)
        LOGGER.info('Final storing probabilities done')
        self._store_info_db(digests, (None, topics_list),
                            db_utils.store_indices_topics, final=True)
        LOGGER.info('Final storing done')

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
            for w in worker:
                w.join()
        else:
            return worker

    def read_files_worker(self, directory, queue):
        """ Read all files in a directory and output to the queue. First line
        of every file should contain the index. Worker separates first line
        and parses to dict. Tuple of index and text is added to queue.

        :directory: Source directory containing files
        :queue: Queue to add the tuples to
        """
        # FIXME: tmp stupid hack due to bad initial design
        for digest, file in enumerate(os.scandir(directory)):
            if file.is_file():
                with open(file.path, 'r', errors='replace') as f:
                    text = f.readlines()
                    try:
                        index = literal_eval(text.pop(0).strip())
                        index['digest'] = 'digest{}'.format(digest)
                        queue.put_nowait((index, '\n'.join(text)))
                    except IndexError:
                        LOGGER.error('File {0} is not classifyable'
                                     .format(file.path))
        LOGGER.info('File reading worker done.')


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
