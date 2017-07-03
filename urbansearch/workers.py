import sys
import os
import logging
import time
from queue import Empty
from multiprocessing import Process, Event
from ast import literal_eval

import config
from urbansearch.gathering import gathering
from urbansearch.filtering import cooccurrence
from urbansearch.clustering import classifytext, text_preprocessor
from urbansearch.utils import db_utils, progress_utils
producers_done = Event()
file_producers_done = Event()
ic_rel_producers_done = Event()

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
                                              kwargs.get('to_db', False),
                                              kwargs.get('progress', False)))
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

    def classifying_worker(self, queue, threshold, to_db, progress=False):
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
                if progress:
                    with progress_utils.counter_lock:
                        progress_utils.counter.value += 1
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

    def classifying_from_files_worker(self, queue, threshold, to_db=False,
                                      progress=False):
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
                if progress:
                    with progress_utils.counter_lock:
                        progress_utils.counter.value += 1
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
        for file in os.scandir(directory):
            if file.is_file():
                with open(file.path, 'r', errors='replace') as f:
                    text = f.readlines()
                    try:
                        index = literal_eval(text.pop(0).strip())
                        queue.put((index, '\n'.join(text)), block=True)
                    except IndexError:
                        LOGGER.error('File {0} is not classifyable'
                                     .format(file.path))
        LOGGER.info('File reading worker done.')

    def run_compute_ic_rels_workers(self, num_workers, queue, join=True):
        """
        Creates workers for computing intercity relations. This method is
        blocking if join is true. Else, it merely returns the created workers.

        :param num_workers: The number of workers to be used
        :param queue: The queue to work from
        :param join: If true, this method blocks until the workers are done
        :return: If join is false, returns the workers. Else, return nothing.
        """
        if num_workers > 1:
            cities = db_utils.city_names()
            size = int(len(cities) / num_workers) + 1

            workers = [Process(target=self.compute_ic_rels_worker,
                               args=(cities[i:i+size], queue))
                       for i in range(num_workers)]
        else:
            workers = [Process(target=self.compute_ic_rels_worker,
                               args=(None, queue)]

        LOGGER.info('Created compute_ic_rels workers')

        for w in workers:
            w.start()

        if join:
            for w in workers:
                w.join()
            LOGGER.info('compute_ic_rels workers done')
        else:
            return workers


    def compute_ic_rels_worker(self, cities, queue):
        """
        Computes the relations for a batch of cities and queues them
        separately.
        :param cities: The list of city names
        :param queue: The queue to append
        """
        relations = {}
        for rel in db_utils.compute_ic_relations(cities):
            relation = (rel['city_a'], rel['city_b'])
            if relation not in relations:
                relations[relation] = {}
            relations[relation][rel['category'].lower()] = rel['score']

        for relation, scores in relations.items():
            queue.put_nowait((relation, scores))
        LOGGER.info('IC relation computer done')

    def run_store_ic_rels_worker(self, queue, join=True, to_db=False):
        """
        Creates and starts a worker for storing intercity relations
        from a queue.
        :param queue: The queue to work from
        :param join: If true, this function blocks untill the worker is done
        If false, the worker is returned
        :param to_db: If true, relations are stored in the database. Else, it
        is seen as a dry run.
        :return: If join=False, the worker is returned. Else, nothing is
        returned
        """
        # Only a single worker, Neo4j didn't seem to be thread-safe sometimes
        worker = [Process(target=self.store_ic_rels_worker,
                          args=(queue, to_db))]
        worker[0].start()

        if join:
            worker[0].join()
        else:
            return worker

    def _commit_ic_rels(self, pairs, values):
        LOGGER.info('Creating IC relations...')
        if not db_utils.store_ic_rels(pairs, values):
            LOGGER.warn('Creating failed for some relations!')
        pairs.clear()
        values.clear()

    def store_ic_rels_worker(self, queue, to_db):
        """
        Stores the intercity relations in the database, iff to_db is
        specified. If not, a dry run is performed.

        :param queue: The queue containing the relations, as pair-scores tuple
        :param to_db: If true, stores the relations in the db.
        Else, it is considered a dry run.
        """
        pairs_list = list()
        values_list = list()

        while not ic_rel_producers_done.is_set():
            time.sleep(1)

        try:
            while not queue.empty():
                pair, values = queue.get(block=True, timeout=5)
                pairs_list.append(pair)
                values_list.append(values)

                if to_db and len(pairs_list) > self.commit:
                    self._commit_ic_rels(pairs_list, values_list)
        except Empty:
            pass

        if to_db:
            self._commit_ic_rels(pairs_list, values_list)

    def set_producers_done(self):
        """ Set the signal that producers are done."""
        global producers_done
        producers_done.set()

    def clear_producers_done(self):
        """ Clear the signal that producers are done."""
        global producers_done
        producers_done.clear()

    def set_file_producers_done(self):
        """ Set the signal that producers are done."""
        global file_producers_done
        file_producers_done.set()

    def clear_file_producers_done(self):
        """ Clear the signal that producers are done."""
        global file_producers_done
        file_producers_done.clear()

    def set_ic_rel_producers_done(self):
        """ Set the signal that producers are done."""
        global ic_rel_producers_done
        ic_rel_producers_done.set()

    def clear_ic_rel_producers_done(self):
        """ Clear the signal that producers are done."""
        global ic_rel_producers_done
        ic_rel_producers_done.clear()
