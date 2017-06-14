import config
from flask import json, jsonify

from urbansearch.server.main import Server

CATEGORIES = config.get('score', 'categories')
s = Server(run=False)


def test_document_route():
    with s.app.test_client() as c:
        resp = c.get('/api/v1/documents')
        data = json.loads(resp.data)

        assert isinstance(data['document'], str)
        assert data['status'] == 200
