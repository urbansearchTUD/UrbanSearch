from flask import Flask
from urbansearch.server.predict import predict_api

API_PREFIX = '/api/v1'

app = Flask(__name__)
app.register_blueprint(simple_page)

class Server(object):
    """
    """
    def __init__(self):
        self.app = Flask(__name__)

        self.app.register_blueprint(predict_api, url_prefix=API_PREFIX)
