import csv
import io
import time
from flask import Blueprint, send_file, request

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
    byteobj = io.BytesIO(fobj.getvalue().encode('utf-8'))

    filename = 'export-{}.csv'.format(name)
    return send_file(byteobj,
            attachment_filename=filename,
            as_attachment=True,
            mimetype='text/csv')


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
