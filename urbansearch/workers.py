import logging
from queue import Empty
from multiprocessing import Process, Event

from urbansearch.gathering import gathering
from urbansearch.clustering import classifytext, text_preprocessor
producers_done = Event()

LOGGER = logging.getLogger(__name__)


class Workers(object):

    """
    Worker class. Contains workers and functions to run workers.
    """

    def __init__(self):
        # global producer_alive
        self.producer_alive = Event()
        self.pd = gathering.PageDownloader()
        self.ct = classifytext.ClassifyText()
        self.prepr = text_preprocessor.PreProcessor()

    def run_classifying_workers(self, no_of_workers, queue, join=True,
                                to_db=False):
        """ Run workers to classify indices consumed from the queue in
        parallel. Workers will only terminate if producers are done, which can
        be signaled setting the producer_done event.

        :no_of_workers: Number of workers that will run
        :queue: multiprocessing.Queue where the indices will be added to
        :join: Wait for workers to be done and join. Default is True.
        parameter
        """
        workers = [Process(target=self.classifying_worker, args=(queue, to_db))
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
        global producers_done

        while not queue.empty() or not producers_done.is_set():
            try:
                index, co_occ = queue.get_nowait()
                txt = self.pd.index_to_txt(index)
                category = self.ct.predict(txt, self.prepr.pre_process)
                prob = self.ct.probability_per_category(txt,
                                                        self.prepr.pre_process)
                if to_db:
                    LOGGER.debug("Inserting {0} for {1} and index: {2}"
                                 .format(prob, co_occ, index))
                    # TODO Call to db_utils
                    # TODO Change logging to debug?
                LOGGER.info("Category: {0} for index {1}".format(str(category),
                                                                 index))
                LOGGER.info("Probabilities: {0} for index {1}".format(str(prob),
                                                                      index))
            except Empty:
                pass

    def set_producers_done(self):
        global producers_done
        producers_done.set()
