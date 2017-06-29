import logging
from multiprocessing import Manager
from argparse import ArgumentParser
from flask import Flask, request
from urbansearch.gathering import indices_selector, gathering
from urbansearch import workers
from urbansearch.utils import db_utils, progress_utils

LOGGER = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/download_indices', methods=['GET'])
def download_indices_for_url(url):
    """ Download all indices for a given url

    :url: String repr of url
    :return: String repr of list of indices
    """
    pd = gathering.PageDownloader()
    url = request.args.get('url')
    collection = request.args.get('collection')
    pd.download_indices(url, collection)
    return str(pd.indices)


@app.route('/classify_documents/log_only', methods=['GET'])
def classify_documents_from_indices(pworkers=1, cworkers=1, directory=None,
                                    threshold=0, progress=False):
    """ Run workers to classify all documents and log only.
    All the indices from the specified directory will be parsed using the
    number of workers specified.

    :pworkers: Number of producing workers, parsing indices and adds to queue.
    :cworkers: Number of consuming workers, classifying indices from the queue.
    :directory: Path to directory containing indices
    """
    try:
        pworkers = int(request.args.get('pworkers', 0))
        cworkers = int(request.args.get('cworkers', 0))
        directory = request.args.get('directory')
        threshold = float(request.args.get('threshold', 0))
    except RuntimeError:
        LOGGER.warning("Not using request")

    if directory:
        LOGGER.info("Using files from dir: {0}".format(directory))

    ind_sel = indices_selector.IndicesSelector()
    cworker = workers.Workers()
    man = Manager()
    queue = man.Queue()

    producers = ind_sel.run_workers(pworkers, directory, queue, join=False,
                                    progress=False)
    consumers = cworker.run_classifying_workers(cworkers, queue, threshold,
                                                join=False, progress=progress)
    if progress:
        progress_utils.print_progress(directory, pre_downloaded=False,
                                      indices_progress=True)

    # Join all workers when done
    _join_workers(cworker, producers, consumers)


@app.route('/classify_documents/to_database', methods=['GET'])
def classify_indices_to_db(pworkers=1, cworkers=1, directory=None,
                           threshold=0, progress=False):
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
    threshold = float(request.args.get('threshold', 0))

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
    consumers = cworker.run_classifying_workers(cworkers, queue, threshold,
                                                join=False, to_db=False,
                                                progress=progress)
    if progress:
        progress_utils.print_progress(directory, pre_downloaded=False)

    # Join all workers when done
    _join_workers(cworker, producers, consumers)


def classify_textfiles_to_db(num_cworkers, directory, threshold, to_db=False,
                             progress=False):
    """ Run workers to classify all documents and output to database.
    Database must be online, all the indices from the specified directory
    will be parsed using the number of workers specified.

    :num_cworkers: Number of consuming workers, classifying indices from the
    queue.
    :directory: Path to directory containing indices
    :to_db: Output results to database specified in config
    """
    if to_db and not db_utils.connected_to_db():
        LOGGER.error("No database connection!")
        return

    if directory:
        LOGGER.info("Using files from dir: {0}".format(directory))

    w_factory = workers.Workers()
    man = Manager()
    queue = man.Queue()

    producer = w_factory.run_read_files_worker(directory, queue, join=False)
    consumers = w_factory.run_classifying_workers(num_cworkers, queue,
                                                  threshold, join=False,
                                                  to_db=to_db,
                                                  pre_downloaded=True,
                                                  progress=progress)

    if progress:
        progress_utils.print_progress(directory, pre_downloaded=True)

    # Join all workers when done
    _join_file_workers(w_factory, producer, consumers)


def create_ic_relations_to_db(num_workers, to_db=False):
    """
    Creates intercity relations and stores them in the database if desired.
    If storing is desired, a connection to the database must be possible.
    Blocks until the producers and workers are done.

    :param num_workers: The number of workers to use for computing the
    relation scores. This is a read-only operation.
    :param to_db: Defaults to false. If true, the relations are stored.
    """
    if to_db and not db_utils.connected_to_db():
        LOGGER.error('No database connection!')
        return

    w_factory = workers.Workers()
    man = Manager()
    queue = man.Queue()

    producers = w_factory.run_compute_ic_rels_workers(num_workers, queue,
                                                      join=False)
    consumers = w_factory.run_store_ic_rels_worker(queue, join=False,
                                                   to_db=to_db)

    # Join all workers when done
    _join_ic_rel_workers(w_factory, producers, consumers)


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


def _join_ic_rel_workers(w, producers, consumers):
    for p in producers:
        p.join()

    # Signal consumers that producers have finished
    w.set_ic_rel_producers_done()

    for c in consumers:
        c.join()

    # Clear event in case it is used again
    w.clear_ic_rel_producers_done()


def _parse_arguments():
    parser = ArgumentParser(description='The TU Delft Urbansearch CLI')

    parser.add_argument('-d', '--directory',
                        help='Source files directory containing files with ' +
                             'indices')

    parser.add_argument('-w', '--workers',
                        help='Number of parallel workers used')

    parser.add_argument('-c', '--config',
                        help='Point to config file that will be used, config' +
                             ' overrides default config')

    parser.add_argument('-z', '--gzipped',
                        help='Only use .gz files available in directory')

    parser.add_argument('-o', '--output',
                        help='Output directory where plain text containing ' +
                             'at least 1 co-occurrence will be stored. By ' +
                             'default the documents will not be stored.')

    parser.add_argument('-opt', '--optimal',
                        help='Try to spawn optimal no. of  workers to put' +
                             ' load on the available CPU\'s')

    parser.add_argument('-v', '--verbose',
                        help='Verbose output, output all debug messages')
    return parser.parse_args()


if __name__ == "__main__":
    # Example call, no output to DB
    classify_textfiles_to_db(2, '/home/gijs/BEP/pages/tmppages/', 0.30, to_db=False, progress=True)
    # create_ic_relations_to_db(1, to_db=True)
    # args = _parse_arguments()
    # directory = '/home/gijs/BEP/test2/'
    # classify_documents_from_indices(8, 2, directory,
    #                                threshold=0, progress=True)
