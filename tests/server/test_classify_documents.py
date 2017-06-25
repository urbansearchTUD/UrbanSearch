from flask import json
from unittest.mock import patch

from urbansearch.gathering.indices_selector import IndicesSelector
from urbansearch.server.main import Server
from urbansearch.server.classify_documents import _join_workers
from urbansearch.workers import Workers

s = Server(run=False)

@patch('urbansearch.server.classify_documents._join_workers')
@patch.object(Workers, 'run_classifying_workers')
@patch.object(IndicesSelector, 'run_workers')
def test_download_indices_for_url(mock_rcw, mock_rw, mock_jw):
    with s.app.test_client() as c:
        resp = c.get('/api/v1/classify_documents/log_only?directory=test')
        data = json.loads(resp.data)

        assert mock_rcw.called
        assert mock_rw.called
        assert mock_jw.called
