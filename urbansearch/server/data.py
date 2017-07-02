import csv
import io
import time
from flask import Blueprint, make_response, request, jsonify

import config
from urbansearch.utils import db_utils

CATEGORIES = config.get('score', 'categories')
HEADER = ['city_a', 'city_b', 'pop_a', 'pop_b', 'dist', 'total', *CATEGORIES]
data_api = Blueprint('data_api', __name__)


def _gen_csv(header, data, name):
    # Creates a CSV response object from given header and data.
    # The download is named export-<name>.csv.
    fobj = io.StringIO()
    writer = csv.DictWriter(fobj, fieldnames=header)
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    filename = 'export-{}.csv'.format(name)
    response = make_response(fobj)
    response.headers['Content-Disposition'] = 'attachment; filename={}'
        .format(filename)
    return response 

@data_api.route('/export_all', methods=['GET'])
def export_all():
    """
    Exports all intercity relations as a CSV download.
    If query parameter "threshold" is provided, only documents
    classified with more than that threshold are taken into account.
    """
    if 'threshold' in request.args:
        return _export_all_with_threshold(request.args.get('threshold'))

    export = db_utils.get_all_ic_rels()
    return _gen_csv(HEADER, export, int(time.time()))


def _export_all_with_threshold(threshold):
    # Counts all relations, so takes a while.
    # Few custom columns: other is removed, filtered_total is added
    export = db_utils.compute_all_ic_rels_with_threshold(threshold)
    relations = {}

    for rel in export:
        relation = (rel['city_a'], rel['city_b'])
        if relation not in relations:
            relations[relation] = {}
            relations[relation]['filtered_total'] = 0
        relations[relation][rel['category'].lower()] = rel['score']
        relations[relation]['pop_a'] = rel['pop_a']
        relations[relation]['pop_b'] = rel['pop_b']
        relations[relation]['dist'] = rel['dist']
        relations[relation]['total'] = rel['total']
        relations[relation]['filtered_total'] += rel['score']

    data = list()
    for rel, scores in relations.items():
        data.append({
            'city_a': rel[0],
            'city_b': rel[1],
            **scores
        })

    header = list(HEADER)
    header.remove('other')
    header.append('filtered_total')
    return _gen_csv(header, data, 'threshold{}'.format(threshold.replace('.', '_')))


@data_api.route('/top_probability/<string:digest>', methods=['GET'])
def top_probability(digest):
    """
    Retrieves the top probability for a given document.

    :param digest: The unique identifier of a document
    :return: A category:probability JSON object
    """
    probabilities = db_utils.get_index_probabilities(digest)
    max_cat = max(probabilities, key=probabilities.get)
    return jsonify({max_cat: probabilities[max_cat]})


@data_api.route('/probabilities/<string:digest>', methods=['GET'])
def probabilities(digest):
    """
    Retrieves the category probabilities for a given document.
    :param digest: the unique identifier of the document
    :return: a JSON object containing all category:probability pairs
    """
    probabilities = db_utils.get_index_probabilities(digest)
    return jsonify(probabilities)
