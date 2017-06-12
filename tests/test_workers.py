import pytest
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch, mock_open
from urbansearch.workers import Workers


@patch('urbansearch.workers.text_preprocessor.PreProcessor')
@patch('urbansearch.workers.cooccurrence.CoOccurrenceChecker')
@patch('urbansearch.workers.classifytext.ClassifyText')
@patch('urbansearch.workers.gathering.PageDownloader')
@patch('urbansearch.workers.Event')
class Test_Mock_Workers(TestCase):

    @patch('urbansearch.workers.Process')
    def test_run_classifying_workers(self, mock_event, mock_pd,
                                     mock_classify, mock_pre_process,
                                     mock_coOc, mock_process):
        queue = Mock()
        workers = Workers()

        mock_pre_process.return_value = Mock()

        # Bugs other fixtures if imported globally.
        from testfixtures import LogCapture
        with LogCapture() as l:
            workers.run_classifying_workers(1, queue)
            assert (l.__sizeof__()) > 0

        assert mock_pre_process.called

    @patch('urbansearch.workers.db_utils')
    def test_classifying_worker(self, mock_db_utils,
                                mock_event, mock_pd, mock_classify,
                                mock_coOc, mock_pre_process):
        queue = MagicMock()
        queue.empty = MagicMock(side_effect=[False, True])
        queue.get = MagicMock(side_effect=[{Mock(), Mock()}])
        w = Workers()
        w._store_ic_rel = Mock()
        w.set_producers_done()

        # Bugs other fixtures if imported globally.
        from testfixtures import LogCapture
        with LogCapture() as l:
            w.classifying_worker(queue, True)
            assert (l.__sizeof__()) > 0

        assert queue.empty.called
        assert queue.get.called
        assert w.pd.index_to_txt.called
        assert w.ct.predict.called
        assert w.ct.probability_per_category.called

    @patch('urbansearch.workers.db_utils.store_ic_rel')
    def test__store_ic_rel(self, mock_db_utils_store_ic,
                           mock_event, mock_pd, mock_classify,
                           mock_coOc, mock_pre_process):
        mock_db_utils_store_ic.return_value = True
        w = Workers()
        w._store_ic_rel([{Mock(), Mock()}])
        assert mock_db_utils_store_ic.called

    @patch('urbansearch.workers.db_utils.store_ic_rel')
    def test__store_ic_rel_no_rel(self, mock_db_utils_store_ic,
                                  mock_event, mock_pd, mock_classify,
                                  mock_coOc, mock_pre_process):
        mock_db_utils_store_ic.return_value = False
        w = Workers()

        from testfixtures import LogCapture
        with LogCapture() as l:
            w._store_ic_rel([{Mock(), Mock()}])
            assert (l.__sizeof__()) > 0

        assert mock_db_utils_store_ic.called

    @patch('urbansearch.workers.db_utils')
    def test_not_classifying_worker(self, mock_db_utils, mock_event, mock_pd,
                                    mock_classify, mock_coOc, mock_pre_process
                                    ):
        queue = MagicMock()
        queue.empty.return_value = True
        queue.get = MagicMock(side_effect=[{Mock(), Mock()}])
        w = Workers()
        w.set_producers_done()

        w.classifying_worker(queue, True)

        assert queue.empty.called
        assert not queue.get.called
        assert not w.pd.index_to_txt.called
        assert not w.ct.predict.called
        assert not w.ct.probability_per_category.called

    @patch('urbansearch.workers.db_utils')
    def test_classifying_from_files_worker(self, mock_db_utils, mock_event,
                                           mock_pd, mock_classify,
                                           mock_coOc, mock_pre_process
                                           ):
        mock_coOc.check.return_value = MagicMock(side_effect=[[[Mock(),
                                                                Mock()]]])

        queue = MagicMock()
        queue.get.return_value = [Mock(), Mock()]
        queue.empty = MagicMock(side_effect=[False, True])
        w = Workers()
        w.set_file_producers_done()
        w._store_ic_rel = Mock()
        w.classifying_from_files_worker(queue, True)

        assert queue.get.called
        assert w.co.check.called
        assert w.ct.probability_per_category.called
        assert mock_db_utils.store_index_probabilities.called

    @patch('urbansearch.workers.literal_eval')
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch('urbansearch.workers.os')
    def test_read_files_worker(self, mock_os, mock_file,
                               mock_lit_ev, mock_event, mock_pd,
                               mock_classify,
                               mock_coOc, mock_pre_process):
        queue = Mock()
        file = Mock()
        f = Mock()
        mock_open.return_value = f

        mock_os.scandir.return_value = [file]
        file.is_file.return_value = True

        w = Workers()
        w.read_files_worker(Mock(), queue)

        assert mock_lit_ev.called
        assert queue.put_nowait.called

    @patch('urbansearch.workers.Process')
    def test_run_read_files_worker(self, mock_process, mock_event, mock_pd,
                                   mock_classify, mock_coOc,
                                   mock_pre_process):

        worker = mock_process.return_value = Mock()
        worker.join.return_value = Mock()

        w = Workers()
        w.run_read_files_worker(Mock(), Mock())

        assert worker.join.called

    @patch('urbansearch.workers.Process')
    def test_run_read_files_worker_join_false(self, mock_process, mock_event,
                                              mock_pd, mock_classify,
                                              mock_coOc, mock_pre_process):
        worker = mock_process.return_value = Mock()
        worker.join.return_value = Mock()

        w = Workers()

        w.run_read_files_worker(Mock(), Mock(), False)

        assert mock_process.called
        assert not worker.join.called
