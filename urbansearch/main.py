from multiprocessing import Manager

from urbansearch.gathering import indices_selector
import logging
LOGGER = logging.getLogger(__name__)

def main():
    LOGGER.info("Started..")
    ind_sel = indices_selector.IndicesSelector()
    man = Manager()
    queue = man.Queue()
    directory = '/home/gijs/BEP/test/'
    ind_sel.run_workers(64, directory, queue)


if __name__ == "__main__":
    main()
