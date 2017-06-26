from flask import json
from unittest.mock import patch, Mock

from urbansearch.gathering.indices_selector import IndicesSelector
from urbansearch.server.main import Server
from urbansearch.server import classify_documents
from urbansearch.server.classify_documents import _join_workers
from urbansearch.workers import Workers

s = Server(run=False)

@patch('urbansearch.server.classify_documents._join_workers')
@patch.object(Workers, 'run_classifying_workers')
@patch.object(IndicesSelector, 'run_workers')
def test_download_indices_for_url(mock_rcw, mock_rw, mock_jw):
    with s.app.test_client() as c:
        resp = c.get('/api/v1/classify_documents/log_only?directory=test')

        assert mock_rcw.called
        assert mock_rw.called
        assert mock_jw.called


@patch('urbansearch.server.classify_documents._join_workers')
@patch.object(Workers, 'run_classifying_workers')
@patch.object(IndicesSelector, 'run_workers')
def test_classify_indices_to_db(mock_rcw, mock_rw, mock_jw):
    with s.app.test_client() as c:
        resp = c.get('/api/v1/classify_documents/to_database?directory=test')

        assert mock_rcw.called
        assert mock_rw.called
        assert mock_jw.called


@patch('urbansearch.server.classify_documents._join_workers')
@patch('urbansearch.server.classify_documents.db_utils')
def test_classify_indices_to_db_no_connection(mock_db, mock_jw):
    mock_db.connected_to_db.return_value = False

    with s.app.test_client() as c:
        resp = c.get('/api/v1/classify_documents/to_database?directory=test')
        assert not mock_jw.called


@patch('urbansearch.server.classify_documents._join_file_workers')
@patch.object(Workers, 'run_classifying_workers')
@patch.object(Workers, 'run_read_files_worker')
def test_classify_textfiles_to_db(mock_rfw, mock_rw, mock_jw):
    classify_documents.classify_textfiles_to_db(0, 'test')

    assert mock_rfw.called
    assert mock_rw.called
    assert mock_jw.called


@patch('urbansearch.server.classify_documents._join_workers')
@patch('urbansearch.server.classify_documents.db_utils')
def test_classify_textfiles_to_db_no_connection(mock_db, mock_jw):
    mock_db.connected_to_db.return_value = False
    classify_documents.classify_textfiles_to_db(0, None)
    assert not mock_jw.called


def test_join_workers():
    producers = [Mock()]
    cworker = Mock()
    consumers = [Mock()]

    classify_documents._join_workers(cworker, producers, consumers)
    
    for p in producers:
        assert p.join.called
    assert cworker.set_producers_done.called
    for c in consumers:
        assert c.join.called
    assert cworker.clear_producers_done.called


def test_join_file_workers():
    producers = [Mock()]
    cworker = Mock()
    consumers = [Mock()]

    classify_documents._join_file_workers(cworker, producers, consumers)
    
    for p in producers:
        assert p.join.called
    assert cworker.set_file_producers_done.called
    for c in consumers:
        assert c.join.called
    assert cworker.clear_file_producers_done.called
