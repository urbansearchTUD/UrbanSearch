import pytest
import json

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
    assert pd._useful_responsecode(index) == exp


def test_cleanindices():
    indices = [json.loads("{\"status\": \"200\"}"),
               json.loads("{\"status\": \"302\"}")]
    assert len(indices) == 2
    pd._clean_indices(indices)
    assert len(indices) == 1
    assert int(indices[0]['status']) == 200


def test_warc_html_to_text():
    with open('%s%s' % (config.get('resources', 'test'), 'warcdata.txt'),
              'rb') as f:
        assert pd.warc_html_to_text(f.read()) == "\r\nTest\r\n\n"


def test_indices_from_file():
    ind = pd.indices_from_file('%s%s' % (config.get('resources', 'test'),
                                         'indices.txt'))
    assert (len(ind)) == 5
    assert ind[0]['digest'] == 'WPTH3FM5VR7UGLA5PZS5L5YI22TNIKXG'


def test_indices_from_gz_file():
    ind = pd.indices_from_gz_file('%s%s' % (config.get('resources', 'test'),
                                            'domain-nl-0000.gz'))
    assert (len(ind)) == 1
    assert ind[0]['digest'] == "3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ"
