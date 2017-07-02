import config
import os
from flask import Blueprint, jsonify, request, make_response
from random import randint

from urbansearch.utils import db_utils
from urbansearch.clustering.classifytext import ClassifyText
from urbansearch.gathering.gathering import PageDownloader

ct = ClassifyText()
pd = PageDownloader()
documents_api = Blueprint('documents_api', __name__)

DATA_DIRECTORY = config.get('resources', 'data')
DOCUMENT_PATH = os.path.join(DATA_DIRECTORY, config.get('api', 'doc_path'))
NUMBER_OF_WORKERS = config.get('api', 'num_of_workers')
NUMBER_OF_DOCUMENTS_PER_WORKER = config.get('api', 'num_of_docs')


def get_categorie(document):
    ct.category_with_threshold(ct.probability_per_category(document), 0.3)


def random_worker():
    return randint(0, NUMBER_OF_WORKERS - 1)


def random_file():
    return randint(0, NUMBER_OF_DOCUMENTS_PER_WORKER - 1)


@documents_api.route('/', methods=['GET'], strict_slashes=False)
def get_random():
    while True:
        try:
            with open(DOCUMENT_PATH.format(random_worker(),
                      random_file())) as f:
                document = f.read()
                if get_categorie(document) != 'Other':
                    break
        except:
            pass

    return jsonify(status=200, document=document)


@documents_api.route('/download', methods=['GET'], strict_slashes=False)
def download():
    """
    Downloads and parses the given document from Common Crawl.
    Requires a request parameter digest.

    :return: The downloaded document
    """
    if 'digest' not in request.args:
        return jsonify(status=400, message='No digest provided!')

    digest = request.args.get('digest')
    index = db_utils.get_index(digest)
    text = pd.index_to_txt(index).split('\n')
    text = '\n'.join(line for line in text if line)

    response = make_response(text)
    response.headers['Content-Disposition'] = 'attachment; filename={}.txt'.format(digest)
    return response
