import pytest
from unittest.mock import MagicMock, Mock, patch
from urbansearch import main


@patch('urbansearch.gathering.gathering.PageDownloader')
def test_mock_download_indices_for_url(mock_gathering_pd,):
    with main.app.app_context():
        with patch('urbansearch.main.request') as mock_flask_request:
            pd = mock_gathering_pd.return_value = Mock()
            main.download_indices_for_url(Mock())
            assert mock_gathering_pd.called
            assert mock_flask_request.args.get.called
            assert pd.download_indices.called
            assert pd.indices_called


@patch('urbansearch.gathering.indices_selector.IndicesSelector')
@patch('urbansearch.workers.Workers')
@patch('urbansearch.main.Manager')
def test_mock_classify_documents_from_indices(mock_manager, mock_workers,
                                         mock_indices_selector):
    with main.app.app_context():
        with patch('urbansearch.main.request') as mock_flask_request:
            ind_sel = mock_indices_selector.return_value = Mock()
            cworker = mock_workers.return_value = Mock()
            man = mock_manager.return_value = Mock()

            a = Mock()
            b = Mock()

            producers = ind_sel.run_workers.return_value = [a, Mock()]
            consumers = cworker.run_classifying_workers.return_value = \
                [b, Mock()]

            # Bugs other fixtures if imported globally.
            from testfixtures import LogCapture
            with LogCapture() as l:
                main.classify_documents_from_indices()
                assert (l.__sizeof__()) > 0

            assert mock_indices_selector.called
            assert mock_workers.called
            assert mock_manager.called
            assert man.Queue.called
            assert ind_sel.run_workers.called
            assert cworker.run_classifying_workers.called
            assert cworker.set_producers_done.called
            assert a.join.called
            assert b.join.called


@patch('urbansearch.utils.db_utils.connected_to_db')
@patch('urbansearch.gathering.indices_selector.IndicesSelector')
@patch('urbansearch.workers.Workers')
@patch('urbansearch.main.Manager')
def test_mock_classify_indices_to_db(mock_manager, mock_workers,
                                     mock_indices_selector,
                                     mock_db_connected):
    with main.app.app_context():
        with patch('urbansearch.main.request') as mock_flask_request:
            ind_sel = mock_indices_selector.return_value = Mock()
            cworker = mock_workers.return_value = Mock()
            man = mock_manager.return_value = Mock()

            mock_db_connected.return_value = True

            a = Mock()
            b = Mock()

            producers = ind_sel.run_workers.return_value = [a, Mock()]
            consumers = cworker.run_classifying_workers.return_value = \
                [b, Mock()]

            # Bugs other fixtures if imported globally.
            from testfixtures import LogCapture
            with LogCapture() as l:
                main.classify_indices_to_db()
                assert (l.__sizeof__()) > 0

            assert mock_indices_selector.called
            assert mock_workers.called
            assert mock_manager.called
            assert man.Queue.called
            assert ind_sel.run_workers.called
            assert cworker.run_classifying_workers.called
            assert cworker.set_producers_done.called
            assert a.join.called
            assert b.join.called


@patch('urbansearch.utils.db_utils.connected_to_db')
def test_mock_classify_indices_to_db_not_connected(mock_db_connected):
    with main.app.app_context():
        with patch('urbansearch.main.request') as mock_flask_request:


            mock_db_connected.return_value = False

            from testfixtures import LogCapture
            with LogCapture() as l:
                main.classify_indices_to_db()
                assert (l.__sizeof__()) > 0


@patch('urbansearch.main.ArgumentParser')
def test_mock_parse_arguments(mock_argumentParser):

    p = mock_argumentParser.return_value = Mock()

    main._parse_arguments()

    assert mock_argumentParser.called
    assert p.add_argument.called
    assert p.parse_args.called
