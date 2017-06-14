from flask import Flask

from urbansearch.server.dataset import dataset_api
from urbansearch.server.documents import documents_api
from urbansearch.server.indices import indices_api
from urbansearch.server.predict import predict_api

API_PREFIX = '/api/v1'


class Server(object):
    """
    Server class which creates a new server and runs it if the run parameter
    is set to True (default).
    """

    def __init__(self, run=True):
        """
        Constructor

        :param run: Boolean value which tells if the app should be started
        or not. In case run is set to True or ommited the app is run, else
        only an app instance is created.
        """

        self.app = Flask(__name__)

        @self.app.route("/")
        def hello():
            return "<h1 style='color:blue'>Hello There!</h1>"


        self.register_blueprints()

        @self.app.after_request
        def apply_caching(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return response

        if run:
            self.app.run()

    def register_blueprints(self):
        """
        Register the predefined blueprints
        """
        self.app.register_blueprint(predict_api,
                                    url_prefix=API_PREFIX + '/classify')
        self.app.register_blueprint(dataset_api,
                                    url_prefix=API_PREFIX + '/datasets')
        self.app.register_blueprint(documents_api,
                                    url_prefix=API_PREFIX + '/documents')
        self.app.register_blueprint(indices_api,
                                    url_prefix=API_PREFIX + '/indices')
