import logging
from argparse import ArgumentParser
from flask import Blueprint, Flask, jsonify, request
from multiprocessing import Manager

from urbansearch.gathering import indices_selector, gathering
from urbansearch import workers
from urbansearch.utils import db_utils

LOGGER = logging.getLogger(__name__)
indices_api = Blueprint('indices_api', __name__)


@indices_api.route('/', methods=['GET'])
@indices_api.route('/download', methods=['GET'])
def download_indices_for_url():
    """ Download all indices for a given url

    :url: String repr of url
    :return: String repr of list of indices
    """
    try:
        pd = gathering.PageDownloader()
        url = request.args.get('url')
        collection = request.args.get('collection')
        pd.download_indices(url, collection)

        return jsonify(indices=str(pd.indices),
                       status=200)
    except:
        return jsonify(error=True,
                       status=500)
