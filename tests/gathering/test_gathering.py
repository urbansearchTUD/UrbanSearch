import json
import os
import requests
import pytest
from multiprocessing import Manager

import config
from urbansearch.gathering import gathering

pd = gathering.PageDownloader()

status_indices = [
    (None, False),
    (json.loads("{\"status\": \"200\"}"), True),
    (json.loads("{\"status\": \"404\"}"), False),
]


@pytest.mark.parametrize("index, exp", status_indices)
def test_responsecode(index, exp):
    assert gathering.PageDownloader._useful_responsecode(index) == exp


def test_cleanindices():
    indices = [json.loads("{\"status\": \"200\"}"),
               json.loads("{\"status\": \"302\"}")]
    assert len(indices) == 2
    pd._clean_indices(indices)
    assert len(indices) == 1
    assert int(indices[0]['status']) == 200


def test_warc_html_to_text():
    with open(os.path.join(config.get('resources', 'test'), 'warcdata.txt'),
              'rb') as f:
        assert pd.warc_html_to_text(f.read()) == "\r\nTest\r\n\n"


def test_warc_html_to_text_exceptions():
    with open(os.path.join(config.get('resources', 'test'), 'indices.txt'),
              'rb') as f:
        assert pd.warc_html_to_text(f.read()) == ""
        assert pd.warc_html_to_text(None) == ""


def test_indices_from_file():
    ind = pd.indices_from_file(os.path.join(config.get('resources', 'test'),
                                            'indices.txt'))
    assert (len(ind)) == 5
    assert ind[0]['digest'] == 'WPTH3FM5VR7UGLA5PZS5L5YI22TNIKXG'


def test_indices_from_gz_file():
    ind = pd.indices_from_gz_file(os.path.join(config.get('resources', 'test'),
                                               'domain-nl-0000.gz'))
    assert (len(ind)) == 1
    assert ind[0]['digest'] == "3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ"


def test_download_indices_exc_empty_url():
    with pytest.raises(ValueError):
        pd.download_indices('', 'test_index')


def test_download_indices_exc_empty_collection():
    with pytest.raises(ValueError):
        pd.download_indices('some.url', '')


def test_download_indices():
    cur_size = len(pd.indices)
    # A bit ugly, but sometimes CommonCrawl is too unresponsive and
    # we do not want our tests to fail because of that
    try:
        pd.download_indices('google.nl', 'CC-MAIN-2017-17-index')
        assert cur_size < len(pd.indices)
    except requests.exceptions.ReadTimeout:
        pass


def test_worker_indices_from_gz_file():
    ind = pd._worker_indices_from_gz_file(os.path.join(config.get('resources', 'test'),
                                               'domain-nl-0000.gz'))
    assert (len(ind)) == 1
    exp = 'crawl-data/CC-MAIN-2017-17/segments/1492917125532.90/crawldiagnostics'\
          '/CC-MAIN-20170423031205-00548-ip-10-145-167-34.ec2.internal.warc.gz'
    assert ind[0]['filename'] == exp


def test_download_warc_part_none():
    assert pd.download_warc_part(None) is None


def test_index_to_txt():
    with open(os.path.join(config.get('resources', 'test'),
                           'text_output.txt'), "r") as text_file:
        exp = text_file.read()
    ind = pd.indices_from_file(os.path.join(config.get('resources', 'test'),
                                            'indices.txt'))
    result = pd.index_to_txt(ind[0])
    assert type(result) == str
    assert result == exp


def test_index_to_raw_text():
    ind = pd.indices_from_file(os.path.join(config.get('resources', 'test'),
                                            'indices.txt'))
    result = pd.index_to_raw_text(ind[0])
    assert type(result) == str
    assert result.splitlines()[0] == 'WARC/1.0'


def test_run_worker_gz():
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    files = [_file.path for _file in os.scandir(directory)
             if _file.is_file() and _file.path.endswith('.gz')]
    pd.worker(queue, files, True)
    index = queue.get_nowait()
    assert index is not None
    # Order is unknown, so allow both possibilities
    assert int(index['offset']) in [727926652, 808]


def test_run_worker():
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    files = [_file.path for _file in os.scandir(directory)
             if _file.is_file() and not _file.path.endswith('.gz')]
    pd.worker(queue, files, False)
    index = queue.get_nowait()
    assert index is not None
    assert int(index['offset']) == 727926652


def test_run_2_workers():
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    pd.run_workers(2, directory, queue)
    index = queue.get_nowait()
    index2 = queue.get_nowait()
    assert index is not None
    assert index2 is not None
    # Order is unknown, so allow both possibilities
    assert int(index['offset']) in [727926652, 808]
    assert int(index2['offset']) in [727926652, 808]


def test_opt_workers():
    man = Manager()
    queue = man.Queue()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    pd.run_workers(1, directory, queue, opt=True)
    index = queue.get_nowait()
    index2 = queue.get_nowait()
    assert index is not None
    assert index2 is not None


def test_remove_keys_empty():
    d = {}
    assert pd._remove_keys(d) == d


def test_remove_key():
    d = {'Ajax': 'Kampioen'}
    assert pd._remove_keys(d) == {}


def test_remove_keys():
    d = {'Ajax': 'Kampioen',
         'length': '1',
         'offset': '2',
         'Feyenoord': 'Niet',
         'filename': 'henk'
         }

    exp = {'length': '1',
           'offset': '2',
           'filename': 'henk'
           }
    assert pd._remove_keys(d) == exp
