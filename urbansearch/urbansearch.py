import logging
from multiprocessing import Manager
from argparse import ArgumentParser
from flask import Flask, request

from urbansearch.gathering import indices_selector

LOGGER = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/workers', methods=['GET'])
def selection_workers():
    LOGGER.info("Started..")
    ind_sel = indices_selector.IndicesSelector()
    man = Manager()
    queue = man.Queue()
    workers = int(request.args.get('workers', 0))
    directory = request.args.get('directory')
    ind_sel.run_workers(workers, directory, queue)
    return "Workers done"


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
    args = parse_arguments()
    print(args)