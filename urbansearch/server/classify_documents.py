import logging
from argparse import ArgumentParser
from flask import Blueprint, jsonify, request
from multiprocessing import Manager

from urbansearch import workers
from urbansearch.gathering import indices_selector, gathering
from urbansearch.utils import db_utils

classify_documents_api = Blueprint('classify_documents_api', __name__)
LOGGER = logging.getLogger(__name__)


@app.route('/log_only', methods=['GET'])
def classify_documents_from_indices(pworkers=1, cworkers=1, directory=None):
    """ Run workers to classify all documents and log only.
    All the indices from the specified directory will be parsed using the
    number of workers specified.

    :pworkers: Number of producing workers, parsing indices and adds to queue.
    :cworkers: Number of consuming workers, classifying indices from the queue.
    :directory: Path to directory containing indices
    """
    pworkers = int(request.args.get('pworkers', 0))
    cworkers = int(request.args.get('cworkers', 0))
    directory = request.args.get('directory')

    if directory:
        LOGGER.info("Using files from dir: {0}".format(directory))

    ind_sel = indices_selector.IndicesSelector()
    cworker = workers.Workers()
    man = Manager()
    queue = man.Queue()

    producers = ind_sel.run_workers(pworkers, directory, queue, join=False)
    consumers = cworker.run_classifying_workers(cworkers, queue, join=False)

    # Join all workers when done
    _join_workers(cworker, producers, consumers)


@app.route('/to_database', methods=['GET'])
def classify_indices_to_db(pworkers=1, cworkers=1, directory=None):
    """ Run workers to classify all documents and output to database.
    Database must be online, all the indices from the specified directory
    will be parsed using the number of workers specified.

    :pworkers: Number of producing workers, parsing indices and adds to queue.
    :cworkers: Number of consuming workers, classifying indices from the queue.
    :directory: Path to directory containing indices
    """
    pworkers = int(request.args.get('pworkers', 0))
    cworkers = int(request.args.get('cworkers', 0))
    directory = request.args.get('directory')

    if not db_utils.connected_to_db():
        LOGGER.error("No database connection!")
        return

    if directory:
        LOGGER.info("Using files from dir: {0}".format(directory))

    ind_sel = indices_selector.IndicesSelector()
    cworker = workers.Workers()
    man = Manager()
    queue = man.Queue()

    producers = ind_sel.run_workers(pworkers, directory, queue, join=False)
    consumers = cworker.run_classifying_workers(cworkers, queue, join=False,
                                                to_db=False)

    # Join all workers when done
    _join_workers(cworker, producers, consumers)


def classify_textfiles_to_db(num_cworkers, directory, to_db=False):
    """ Run workers to classify all documents and output to database.
    Database must be online, all the indices from the specified directory
    will be parsed using the number of workers specified.

    :num_cworkers: Number of consuming workers, classifying indices from the
    queue.
    :directory: Path to directory containing indices
    :to_db: Output results to database specified in config
    """
    if not db_utils.connected_to_db():
        LOGGER.error("No database connection!")
        return

    if directory:
        LOGGER.info("Using files from dir: {0}".format(directory))

    w_factory = workers.Workers()
    man = Manager()
    queue = man.Queue()

    producer = w_factory.run_read_files_worker(directory, queue, join=False)
    consumers = w_factory.run_classifying_workers(num_cworkers, queue,
                                                  join=False, to_db=False,
                                                  pre_downloaded=True)

    # Join all workers when done
    _join_file_workers(w_factory, producer, consumers)


def _join_workers(cworker, producers, consumers):
    # Wait for producers to finish
    for p in producers:
        p.join()

    # Signal consumers that producers have finished
    cworker.set_producers_done()

    for c in consumers:
        c.join()

    # Clear event in case cworker is used again
    cworker.clear_producers_done()


def _join_file_workers(w, producers, consumers):
    # Wait for producers to finish
    for p in producers:
        p.join()
    # Signal consumers that producers have finished
    w.set_file_producers_done()

    for c in consumers:
        c.join()

    # Clear event in case it is used again
    w.clear_file_producers_done()
