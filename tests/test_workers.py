import pytest
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch
from urbansearch.workers import Workers


@patch('urbansearch.clustering.text_preprocessor.PreProcessor')
@patch('urbansearch.clustering.classifytext.ClassifyText')
@patch('urbansearch.gathering.gathering.PageDownloader')
@patch('urbansearch.workers.Event')
class Test_Workers(TestCase):


    @patch('urbansearch.workers.Process')
    def test_mock_run_classifying_workers(self, mock_event, mock_pd, mock_classify, mock_pre_process, mock_process):
        queue = Mock()

        workers = Workers()

        mock_pre_process.return_value = Mock()

        # Bugs other fixtures if imported globally.
        from testfixtures import LogCapture
        with LogCapture() as l:
            workers.run_classifying_workers(1, queue)
            assert (l.__sizeof__()) > 0

        assert mock_pre_process.called


    @patch('urbansearch.utils.db_utils')
    @patch('queue.Empty')
    def test_mock_classifying_worker(self, mock_event, mock_pd, mock_classify, mock_pre_process, mock_q_empty, mock_db_utils):
        queue = Mock()
        queue.empty = MagicMock(side_effect=[False, True])
        co_oc_mock = MagicMock(side_effect=[[{Mock()}, {Mock()}]])
        queue.get_nowait = MagicMock(side_effect=[{Mock(), co_oc_mock}])
        w = Workers()
        w.set_producers_done()

        mock_db_utils.store_index_probabilities = Mock()

        # Bugs other fixtures if imported globally.
        from testfixtures import LogCapture
        with LogCapture() as l:
            w.classifying_worker(queue, True)
            assert (l.__sizeof__()) > 0

        assert queue.empty.called
        assert queue.get_nowait.called
        assert w.pd.index_to_txt.called
        assert w.ct.predict.called
        assert w.ct.probability_per_category.called

