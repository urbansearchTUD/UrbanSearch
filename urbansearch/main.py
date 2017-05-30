import logging
from multiprocessing import Manager
from argparse import ArgumentParser
from flask import Flask, request
from itertools import chain
from urbansearch.gathering import indices_selector, gathering
from urbansearch import workers

LOGGER = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/workers', methods=['GET'])
def selection_workers():
    ind_sel = indices_selector.IndicesSelector()
    man = Manager()
    queue = man.Queue()
    iworkers = int(request.args.get('workers', 0))
    directory = request.args.get('directory')
    ind_sel.run_workers(iworkers, directory, queue)
    return "Workers done"


@app.route('/download_indices', methods=['GET'])
def download_indices_for_url():
    pd = gathering.PageDownloader()
    url = request.args.get('url')
    collection = request.args.get('collection')
    pd.download_indices(url, collection)
    return str(pd.indices)


def classify_documents_from_indices():
    # pworkers = int(request.args.get('pworkers', 0))
    # cworkers = int(request.args.get('cworkers', 0))
    # directory = request.args.get('directory')
    pworkers = 4
    cworkers = 2
    directory = '/home/gijs/BEP/test2/'
    ind_sel = indices_selector.IndicesSelector()
    cworker = workers.Workers()
    man = Manager()
    queue = man.Queue()
    producers = ind_sel.run_workers(pworkers, directory, queue, join=False)
    consumers = cworker.run_classifying_workers(cworkers, queue, join=False)
    # Join all workers when done
    _join_workers(cworker, producers, consumers)


def _join_workers(cworker, producers, consumers):
    for p in producers:
        p.join()

    # Signal consumers that producers have finished
    cworker.set_producers_done()

    for c in consumers:
        c.join()


def parse_arguments():
    parser = ArgumentParser(description='The TU Delft Urbansearch CLI')

    parser.add_argument('-d', '--directory',
                        help='Source files directory containing files with '
                              + 'indices')

    parser.add_argument('-w', '--workers',
                        help='Number of parallel workers used')

    parser.add_argument('-c', '--config',
                        help='Point to config file that will be used, config '
                             + 'overrides default config')

    parser.add_argument('-z', '--gzipped',
                        help='Only use .gz files available in directory')

    parser.add_argument('-o', '--output',
                        help='Output directory where plain text containing at '
                             + 'least 1 co-occurrence will be stored. By '
                             + 'default the documents will not be stored.')

    parser.add_argument('-opt', '--optimal',
                        help='Try to spawn optimal no. of  workers to put full'
                             + ' load on the available CPU\'s')

    parser.add_argument('-v', '--verbose',
                        help='Verbose output, output all debug messages')
    return parser.parse_args()


if __name__ == "__main__":
    classify_documents_from_indices()
    # args = parse_arguments()
    # print(args)
