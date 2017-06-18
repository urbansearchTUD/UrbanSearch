import pytest
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch, mock_open
from urbansearch.workers import Workers


@patch('config.get')
@patch('urbansearch.workers.text_preprocessor.PreProcessor')
@patch('urbansearch.workers.cooccurrence.CoOccurrenceChecker')
@patch('urbansearch.workers.classifytext.ClassifyText')
@patch('urbansearch.workers.gathering.PageDownloader')
@patch('urbansearch.workers.Event')
class Test_Workers(TestCase):

    @patch('urbansearch.workers.Process')
    def test_run_classifying_workers(self, mock_event, mock_pd,
                                     mock_classify, mock_pre_process,
                                     mock_coOc, mock_config,
                                     mock_process):
        queue = Mock()
        w = Workers()

        mock_pre_process.return_value = Mock()

        # Bugs other fixtures if imported globally.
        from testfixtures import LogCapture
        with LogCapture() as l:
            w.run_classifying_workers(1, queue, 1, pre_downloaded=True)
            assert (l.__sizeof__()) > 0
            assert mock_pre_process.called

    @patch('urbansearch.workers.db_utils')
    def test_classifying_worker(self, mock_db_utils, mock_event,
                                mock_pd, mock_classify, mock_coOc,
                                mock_pre_process, mock_config):
        queue = MagicMock()
        queue.empty = MagicMock(side_effect=[False, True])
        queue.get = MagicMock(side_effect=[{Mock(), Mock()}])
        mock_config.return_value = 0
        w = Workers()
        w._store_indices_db = Mock()
        w._store_info_db = Mock()
        w._final_store_db = Mock()
        w.set_producers_done()

        # Bugs other fixtures if imported globally.
        from testfixtures import LogCapture
        with LogCapture() as l:
            w.classifying_worker(queue, 1, True)
            assert (l.__sizeof__()) > 0

        assert queue.empty.called
        assert queue.get.called
        assert w.pd.index_to_txt.called
        assert w.ct.probability_per_category.called
        assert w.ct.categories_above_threshold.called
        assert w._store_indices_db.called
        assert w._store_info_db.called
        assert w._final_store_db.called

    @patch('urbansearch.workers.db_utils')
    def test_not_classifying_worker(self, mock_db_utils, mock_event, mock_pd,
                                    mock_classify, mock_coOc,  mock_config,
                                    mock_pre_process):
            queue = MagicMock()
            queue.empty.return_value = True
            queue.get = MagicMock(side_effect=[{Mock(), Mock()}])
            w = Workers()
            w._store_indices_db = Mock()
            w._store_info_db = Mock()
            w._final_store_db = Mock()
            w.set_producers_done()

            w.classifying_worker(queue, 1, True)

            assert queue.empty.called
            assert not queue.get.called
            assert not w.pd.index_to_txt.called
            assert not w.ct.probability_per_category.called
            assert not w.ct.categories_above_threshold.called
            assert not w._store_indices_db.called
            assert not w._store_info_db.called
            assert w._final_store_db.called

    @patch('urbansearch.workers.db_utils')
    def test_classifying_from_files_worker(self, mock_db_utils, mock_event,
                                           mock_pd, mock_classify,
                                           mock_coOc, mock_pre_process,
                                           mock_config
                                           ):
        mock_coOc.check.return_value = MagicMock(side_effect=[[[Mock(),
                                                                Mock()]]])

        queue = MagicMock()
        queue.get.return_value = [Mock(), Mock()]
        queue.empty = MagicMock(side_effect=[False, True])
        mock_config.return_value = 0
        w = Workers()
        w._store_indices_db = Mock()
        w._store_info_db = Mock()
        w._final_store_db = Mock()
        w.set_file_producers_done()
        w.classifying_from_files_worker(queue, 1, True)

        assert queue.get.called
        assert w.co.check.called
        assert w.ct.probability_per_category.called
        assert w.ct.categories_above_threshold.called
        assert w._store_indices_db.called
        assert w._store_info_db.called
        assert w._final_store_db.called

    @patch('urbansearch.workers.literal_eval')
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch('urbansearch.workers.os')
    def test_read_files_worker(self, mock_os, mock_file,
                               mock_lit_ev, mock_event, mock_pd,
                               mock_classify,
                               mock_coOc, mock_config, mock_pre_process):
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
                                   mock_classify, mock_coOc, mock_config,
                                   mock_pre_process):

        worker = mock_process.return_value = Mock()
        worker.join.return_value = Mock()

        w = Workers()
        w.run_read_files_worker(Mock(), Mock())

        assert worker.join.called

    @patch('urbansearch.workers.Process')
    def test_run_read_files_worker_join_false(self, mock_process, mock_event,
                                              mock_pd, mock_classify,
                                              mock_coOc, mock_config,
                                              mock_pre_process):
        worker = mock_process.return_value = Mock()
        worker.join.return_value = Mock()

        w = Workers()

        w.run_read_files_worker(Mock(), Mock(), False)

        assert mock_process.called
        assert not worker.join.called

    @patch('urbansearch.workers.db_utils')
    def test__store_indices_db(self, mock_db, mock_event,
                               mock_pd, mock_classify,
                               mock_coOc, mock_pre_process,
                               mock_config):
        mock_index = Mock(return_value=True)
        mock_indice = MagicMock()
        mock_indice.return_value = True
        mock_indice.__len__.return_value = 40001
        mock_config.return_value = 0
        mock_db.store_indices.return_value = False

        w = Workers()
        from testfixtures import LogCapture
        with LogCapture() as l:
            w._store_indices_db(mock_index, mock_indice)
            assert (l.__sizeof__()) > 0
            assert mock_indice.append.called
            assert mock_db.store_indices.called
            assert mock_indice.clear.called

    @patch('urbansearch.workers.db_utils')
    def test__store_indices_db_index_none(self, mock_db, mock_event,
                                          mock_pd, mock_classify,
                                          mock_coOc, mock_pre_process,
                                          mock_config):
        mock_index = Mock(return_value=None)
        mock_indice = MagicMock()
        mock_indice.__len__.return_value = 0
        mock_config.return_value = 1

        w = Workers()
        w._store_indices_db(None, mock_indice, True)

        assert not mock_indice.append.called
        assert mock_db.store_indices.called
        assert not mock_indice.clear.called

    def test__store_info_db(self, mock_event,
                            mock_pd, mock_classify,
                            mock_coOc, mock_pre_process,
                            mock_config):
        mock_config.return_value = 0

        mock_digests = Mock()
        mock_itm = Mock()
        mock_list = MagicMock()
        mock_list.__len__.return_value = 1
        mock_item = [mock_itm, mock_list]
        util_func = Mock()
        util_func.__name__ = 'mocked_util_func'

        w = Workers()
        from testfixtures import LogCapture
        with LogCapture() as l:
            w._store_info_db(mock_digests, mock_item, util_func)
            assert (l.__sizeof__()) > 0
            assert mock_list.append.called
            assert mock_list.clear.called

    def test__store_info_db_not_item(self, mock_event,
                                     mock_pd, mock_classify,
                                     mock_coOc, mock_pre_process,
                                     mock_config):
        util_func = Mock()
        w = Workers()
        w._store_info_db(Mock(), [False, False], util_func)
        assert not util_func.called

    def test__store_info_db_final(self, mock_event,
                                  mock_pd, mock_classify,
                                  mock_coOc, mock_pre_process,
                                  mock_config):
        mock_util_func = Mock()
        w = Workers()
        w._store_info_db(Mock(), [None, True], mock_util_func, True)
        assert mock_util_func.called

    def test__final_store_db(self, mock_event,
                             mock_pd, mock_classify,
                             mock_coOc, mock_pre_process,
                             mock_config):
        mock_config.return_value = 0
        data_lists = MagicMock(return_value=[Mock(), Mock(), Mock(),
                                             Mock(), Mock()])
        w = Workers()

        w._store_indices_db = Mock()
        w._store_info_db = Mock()

        w._final_store_db(data_lists)

        assert w._store_indices_db.called
        assert w._store_info_db.called
