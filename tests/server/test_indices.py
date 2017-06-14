from flask import json
from unittest.mock import patch
from urbansearch import main

from urbansearch.gathering.gathering import PageDownloader
from urbansearch.server.main import Server

s = Server(run=False)


@patch.object(PageDownloader, 'download_indices')
def test_download_indices_for_url(mock_di,):
    with s.app.test_client() as c:
        resp = c.get('/api/v1/indices')
        data = json.loads(resp.data)

        assert data['status'] == 200
        assert isinstance(data['indices'], str)
        assert mock_di.called
