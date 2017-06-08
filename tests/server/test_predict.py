import config
from flask import json, jsonify

from urbansearch.server.main import Server

CATEGORIES = config.get('score', 'categories')
s = Server(run=False)


def test_classify_route():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify',
                      data=json.dumps({'document': 'onderwijs school'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 200
        assert data['category'] in CATEGORIES


def test_predict_route():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify/predict',
                      data=json.dumps({'document': 'onderwijs school'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 200
        assert data['category'] in CATEGORIES


def test_classify_route_error():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify',
                      data=json.dumps({'faulty': 'onderwijs school'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 500
        assert isinstance(data['message'], str)
        assert data['error']


def test_predict_route_error():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify/predict',
                      data=json.dumps({'faulty': 'onderwijs school'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 500
        assert isinstance(data['message'], str)
        assert data['error']


def test_classify_route_no_json():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify')
        data = json.loads(resp.data)

        assert data['status'] == 400
        assert isinstance(data['message'], str)
        assert data['error']


def test_predict_route_no_json():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify/predict')
        data = json.loads(resp.data)

        assert data['status'] == 400
        assert isinstance(data['message'], str)
        assert data['error']

def test_probabilities_route():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify/probabilities',
                      data=json.dumps({'document': 'test string'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 200
        for key, value in data['probabilities'].items():
            assert key in CATEGORIES

def test_probabilities_route_error():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify/probabilities',
                      data=json.dumps({'faulty': 'test string'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 500
        assert isinstance(data['message'], str)
        assert data['error']

def test_probabilities_route_no_json():
    with s.app.test_client() as c:
        resp = c.post('/api/v1/classify/probabilities')
        data = json.loads(resp.data)

        assert data['status'] == 400
        assert isinstance(data['message'], str)
        assert data['error']
