import os
from multiprocessing import Manager

from urbansearch.gathering import indices_selector
import config


def test_irrelevant_indices_from_gz_file():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    _file = os.path.join(config.get('resources', 'test'), 'domain-nl-0000.gz')
    relevant = ind_sel.relevant_indices_from_file(_file)
    assert len(relevant) == 0


def test_relevant_indices_from_gz_file():
    ind_sel = indices_selector.IndicesSelector(cities=['Rotterdam',
                                                       'Wassenaar'])
    _file = os.path.join(config.get('resources', 'test'), 'relevant.gz')
    relevant = ind_sel.relevant_indices_from_file(_file)
    assert len(relevant) == 1


def test_relevant_indices_from_other_file():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    _file = os.path.join(config.get('resources', 'test'), 'indices2.txt')
    relevant = ind_sel.relevant_indices_from_file(_file)
    assert len(relevant) == 1


def test_relevant_indices_from_dir():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    assert len(ind_sel.page_downloader.indices) == 0
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    relevant = ind_sel.relevant_indices_from_dir(directory)
    assert len(relevant) == 2
    assert relevant[0]['digest'] == 'WPTH3FM5VR7UGLA5PZS5L5YI22TNIKXG'


def test_run_worker():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    files = [_file.path for _file in os.scandir(directory)
             if _file.is_file()]
    ind_sel.worker(queue, files)
    index = queue.get_nowait()
    assert index is not None
    assert int(index['status']) == 200
    assert index['digest'] == 'WPTH3FM5VR7UGLA5PZS5L5YI22TNIKXG'


def test_run_2_workers():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    ind_sel.run_workers(2, directory, queue)
    index = queue.get_nowait()
    index2 = queue.get_nowait()
    assert index is not None
    assert index2 is not None
    exp = 'crawl-data/CC-MAIN-2017-13/segments/1490218187144.60/warc/'\
          'CC-MAIN-20170322212947-00594-ip-10-233-31-227.ec2.internal.warc.gz'
    assert index['filename'] == exp
    assert index2['filename'] == exp


def test_run_odd_workers():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    ind_sel.run_workers(3, directory, queue)
    index = queue.get_nowait()
    index2 = queue.get_nowait()
    assert index is not None
    assert index2 is not None
    exp = 'crawl-data/CC-MAIN-2017-13/segments/1490218187144.60/warc/'\
          'CC-MAIN-20170322212947-00594-ip-10-233-31-227.ec2.internal.warc.gz'
    assert index['filename'] == exp
    assert index2['filename'] == exp


def test_run_opt_workers():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    ind_sel.run_workers(2, directory, queue, opt=True)
    index = queue.get_nowait()
    index2 = queue.get_nowait()
    assert index is not None
    assert index2 is not None
    exp = 'crawl-data/CC-MAIN-2017-13/segments/1490218187144.60/warc/'\
          'CC-MAIN-20170322212947-00594-ip-10-233-31-227.ec2.internal.warc.gz'
    assert index['filename'] == exp
    assert index2['filename'] == exp
