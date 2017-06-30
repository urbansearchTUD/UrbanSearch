from flask import json
from unittest.mock import patch, Mock

from urbansearch.gathering.indices_selector import IndicesSelector
from urbansearch.server.main import Server
from urbansearch.server import classifier
from urbansearch.workers import Workers

s = Server(run=False)

@patch('urbansearch.server.classifier.dpu')
@patch('urbansearch.server.classifier.smm')
def test_train(smm, dpu):
    classifier.dpu = Mock()
    classifier.dpu.load.return_value = {'inputs': [], 'outputs': []}
    classifier.smm = Mock()

    with s.app.test_client() as c:
        resp = c.post('/api/v1/classifier/train?default=true')
        assert classifier.dpu.generate_dataset.called
        assert classifier.dpu.load.called
        # assert classifier.smm.train.called

        assert json.loads(resp.data) == {'status': 200, 'message': 'success'}


@patch('urbansearch.server.classifier.dpu')
@patch('urbansearch.server.classifier.smm')
def test_train_no_default(smm, dpu):
    classifier.dpu = Mock()
    classifier.dpu.load.return_value = {'inputs': [], 'outputs': []}
    classifier.smm = Mock()

    with s.app.test_client() as c:
        resp = c.post('/api/v1/classifier/train')
        assert classifier.dpu.generate_dataset.called
        assert classifier.dpu.load.called
        # assert classifier.smm.train.called

        assert json.loads(resp.data) == {'status': 200, 'message': 'success'}


@patch('urbansearch.server.classifier.SGDCModelManager')
def test_train_equal(mm):
    classifier.dpu = Mock()
    classifier.dpu.load.return_value = {'inputs': [], 'outputs': []}

    with s.app.test_client() as c:
        resp = c.post('/api/v1/classifier/train_equal?default=true')
        assert classifier.dpu.generate_equal_dataset.called
        assert classifier.dpu.load.called

        assert json.loads(resp.data) == {'status': 200, 'message': 'success'}


@patch('urbansearch.server.classifier.SGDCModelManager')
def test_train_equal_no_default(mm):
    classifier.dpu = Mock()
    classifier.dpu.load.return_value = {'inputs': [], 'outputs': []}

    with s.app.test_client() as c:
        resp = c.post('/api/v1/classifier/train_equal')
        assert classifier.dpu.generate_equal_dataset.called
        assert classifier.dpu.load.called

        data = json.loads(resp.data)
        assert data['status'] == 200
        assert data['message'] == 'success'


@patch('urbansearch.server.classifier.SGDCModelManager')
def test_train_test_equal(mm):
    classifier.dpu = Mock()
    classifier.dpu.load.return_value = {'inputs': [], 'outputs': []}
    mm.score.return_value = 0

    with s.app.test_client() as c:
        resp = c.post('/api/v1/classifier/train_test_equal')
        assert classifier.dpu.generate_equal_dataset.called
        assert classifier.dpu.load.called


@patch('urbansearch.server.classifier.SGDCModelManager')
@patch('urbansearch.server.classifier.classification_report')
def test_metrics_equal(cr, mm):
    cr.return_value = 'success'
    classifier.dpu = Mock()
    classifier.dpu.load.return_value = {'inputs': [], 'outputs': []}

    with s.app.test_client() as c:
        resp = c.get('/api/v1/classifier/metrics_equal')
        assert classifier.dpu.generate_equal_dataset.called
        assert classifier.dpu.load.called

        data = json.loads(resp.data)
        assert data['status'] == 200
        assert data['message'] == 'success'


@patch('urbansearch.server.classifier.SGDCModelManager')
@patch('urbansearch.server.classifier.classification_report')
def test_probabilities_equal(cr, mm):
    cr.return_value = 'success'
    classifier.dpu = Mock()
    classifier.dpu.load.return_value = {'inputs': [], 'outputs': []}

    with s.app.test_client() as c:
        resp = c.get('/api/v1/classifier/probabilities_equal')
        assert classifier.dpu.generate_equal_dataset.called
        assert classifier.dpu.load.called

        data = json.loads(resp.data)
        assert data['status'] == 200
