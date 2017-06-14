import logging
from multiprocessing import Manager
from argparse import ArgumentParser
from flask import Flask, request
from urbansearch.gathering import indices_selector, gathering
from urbansearch import workers
from urbansearch.utils import db_utils

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
                                    threshold=0):
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
    threshold = float(request.args.get('threshold', 0))

    if directory:
        LOGGER.info("Using files from dir: {0}".format(directory))

    ind_sel = indices_selector.IndicesSelector()
    cworker = workers.Workers()
    man = Manager()
    queue = man.Queue()

    producers = ind_sel.run_workers(pworkers, directory, queue, join=False)
    consumers = cworker.run_classifying_workers(cworkers, queue, threshold,
                                                join=False)

    # Join all workers when done
    _join_workers(cworker, producers, consumers)


@app.route('/classify_documents/to_database', methods=['GET'])
def classify_indices_to_db(pworkers=1, cworkers=1, directory=None,
                           threshold=0):
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
                                                join=False, to_db=False)

    # Join all workers when done
    _join_workers(cworker, producers, consumers)


def classify_textfiles_to_db(num_cworkers, directory, threshold, to_db=False):
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
                                                  threshold, join=False,
                                                  to_db=False,
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
    classify_textfiles_to_db(2, '/files/directory/', 0.35, to_db=False)
    # args = _parse_arguments()

    # TODO Create CLI, make different PR
