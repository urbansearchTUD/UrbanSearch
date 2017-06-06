from flask import Flask
from urbansearch.server.predict import predict_api

API_PREFIX = '/api/v1'
class Server(object):
    """
    """
    def __init__(self, run=True):
        self.app = Flask(__name__)
        self.register_blueprints()

        if run:
            self.app.run()

    def register_blueprints():
        self.app.register_blueprint(predict_api, url_prefix=API_PREFIX)
