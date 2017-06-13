import config
import os
from flask import Blueprint, jsonify, request
from random import randint

documents_api = Blueprint('documents_api', __name__)

DATA_DIRECTORY = config.get('resources', 'data')
DOCUMENT_PATH = os.path.join(DATA_DIRECTORY, config.get('api', 'doc_path'))
NUMBER_OF_WORKERS = config.get('api', 'num_of_workers')
NUMBER_OF_DOCUMENTS_PER_WORKER = config.get('api', 'num_of_docs')


def random_worker():
    return randint(0, NUMBER_OF_WORKERS - 1)


def random_file():
    return randint(0, NUMBER_OF_DOCUMENTS_PER_WORKER - 1)


@documents_api.route('/', methods=['GET'], strict_slashes=False)
def get_random():
    """
    """
    while True:
        try:
            with open(DOCUMENT_PATH.format(random_worker(),
                      random_file())) as f:
                document = f.read()
                break
        except:
            pass

    return jsonify(status=200, document=document)


@documents_api.route('/test', methods=['GET'], strict_slashes=False)
def get_random_test():
    """
    """
    while True:
        try:
            path = DOCUMENT_PATH.format(randint(0, 1),randint(0, 1))
            with open(path) as f:
                document = f.read()
                break
        except:
            pass

    return jsonify(status=200, document=document)
