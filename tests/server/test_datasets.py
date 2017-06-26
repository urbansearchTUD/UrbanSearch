import config
from flask import json, jsonify
from unittest.mock import patch

from urbansearch.utils.dataset_p_utils import DatasetPickleUtils
from urbansearch.server.main import Server

CATEGORIES = config.get('score', 'categories')
s = Server(run=False)

@patch.object(DatasetPickleUtils, 'append_to_inputs')
def test_append_route(append_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/append',
                      data=json.dumps({'document': 'onderwijs school',
                                        'category': 'education'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 200
        assert append_mock.called


@patch.object(DatasetPickleUtils, 'append_to_inputs')
def test_append_route_error(append_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/append',
                      data=json.dumps({'faulty': 'onderwijs school',
                                        'category': 'education'}),
                      content_type='application/json')
        data = json.loads(resp.data)

        assert data['status'] == 400
        assert not append_mock.called


@patch.object(DatasetPickleUtils, 'append_to_inputs')
def test_append_route_no_json(append_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/append')
        data = json.loads(resp.data)

        assert data['status'] == 400
        assert not append_mock.called


@patch.object(DatasetPickleUtils, 'append_to_inputs')
def test_append_all(append_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/append_all', data=json.dumps({
            'document': 'test',
            'categories': ['education', 'transportation']}),
            content_type='application/json'
            )
        data = json.loads(resp.data)

        assert data['status'] == 200

        append_mock.assert_any_call('test', category='education')
        append_mock.assert_any_call('test', category='transportation')

@patch.object(DatasetPickleUtils, 'append_to_inputs')
def test_append_all_error(append_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/append_all', data=json.dumps({
            'faulty': 'test',
            'fault': ''}),
            content_type='application/json'
            )
        data = json.loads(resp.data)

        assert data['status'] == 400

@patch.object(DatasetPickleUtils, 'generate_dataset')
def test_create_route(create_mock):
    with s.app.test_client() as c:
        resp = c.get('/api/v1/datasets/create')
        data = json.loads(resp.data)

        assert data['status'] == 200
        assert create_mock.called


@patch.object(DatasetPickleUtils, 'init_categoryset')
def test_create_categoryset_route(create_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/create/categoryset',
                      data=json.dumps({'documents': [],
                                        'category': 'education'}),
                      content_type='application/json')

        data = json.loads(resp.data)

        assert data['status'] == 200
        assert create_mock.called


@patch.object(DatasetPickleUtils, 'init_categoryset')
def test_create_categoryset_route_error(create_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/create/categoryset',
                      data=json.dumps({'faulty': [],
                                        'category': 'education'}),
                      content_type='application/json')

        data = json.loads(resp.data)

        assert data['status'] == 500
        assert not create_mock.called


@patch.object(DatasetPickleUtils, 'init_categoryset')
def test_create_categoryset_route_no_json(create_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/create/categoryset')

        data = json.loads(resp.data)

        assert data['status'] == 400
        assert not create_mock.called

@patch.object(DatasetPickleUtils, 'init_categorysets')
def test_init_categorysets(create_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/init_categorysets')

        data = json.loads(resp.data)

        assert data['status'] == 200
        assert create_mock.called

@patch.object(DatasetPickleUtils, 'load')
def test_lengths(load_mock):
    load_mock.return_value = {'inputs': ['test']}
    with s.app.test_client() as c:
        resp = c.get('/api/v1/datasets/lengths')

        data = json.loads(resp.data)
        print(data['lengths'])
        assert data['status'] == 200

@patch.object(DatasetPickleUtils, 'persist_categorysets')
def test_persist_categorysets(persist_mock):
    with s.app.test_client() as c:
        resp = c.post('/api/v1/datasets/persist/categorysets')

        data = json.loads(resp.data)

        assert data['status'] == 200
        assert persist_mock.called
