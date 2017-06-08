import pytest
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch
from urbansearch.workers import Workers


@patch('urbansearch.workers.text_preprocessor.PreProcessor')
@patch('urbansearch.workers.classifytext.ClassifyText')
@patch('urbansearch.workers.gathering.PageDownloader')
@patch('urbansearch.workers.Event')
class Test_Mock_Workers(TestCase):

    @patch('urbansearch.workers.Process')
    def test_mock_run_classifying_workers(self, mock_event, mock_pd,
                                          mock_classify,
                                          mock_pre_process, mock_process):
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
    def test_mock_classifying_worker(self, mock_event, mock_pd, mock_classify,
                                     mock_pre_process, mock_db_utils):
        queue = MagicMock()
        queue.empty = MagicMock(side_effect=[False, True])
        queue.get_nowait = MagicMock(side_effect=[Mock(), Mock(return_value=iter([]))])
        w = Workers()
        w.set_producers_done()
        w.clear_producers_done()

        # Bugs other fixtures if imported globally.
        from testfixtures import LogCapture
        with LogCapture() as l:
            w.classifying_worker(queue, True)
            assert (l.__sizeof__()) == 0

        assert queue.empty.called
        assert queue.get_nowait.called
        assert w.pd.index_to_txt.called
        assert w.ct.predict.called
        assert w.ct.probability_per_category.called

    @patch('urbansearch.workers.db_utils')
    def test_mock_not_classifying_worker(self, mock_event, mock_pd, mock_classify,
                                     mock_pre_process, mock_db_utils):
        queue = MagicMock()
        queue.empty.return_value = True
        queue.get_nowait = MagicMock(side_effect=[{Mock(), Mock()}])
        w = Workers()
        w.set_producers_done()

        w.classifying_worker(queue, True)

        assert queue.empty.called
        assert not queue.get_nowait.called
        assert not w.pd.index_to_txt.called
        assert not w.ct.predict.called
        assert not w.ct.probability_per_category.called



