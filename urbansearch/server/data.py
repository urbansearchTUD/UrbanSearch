import csv
import io
import time
from flask import Blueprint, send_file

import config
from urbansearch.utils import db_utils

CATEGORIES = config.get('score', 'categories')
data_api = Blueprint('data_api', __name__)


@data_api.route('/export_all', methods=['GET'])
def export_all():
    export = db_utils.get_all_ic_rels()

    header = ['city_a', 'city_b', 'pop_a', 'pop_b', 'dist', 'total', *CATEGORIES]
    fobj = io.StringIO()
    writer = csv.DictWriter(fobj, fieldnames=header)
    writer.writeheader()
    for row in export:
        writer.writerow(row)
    byteobj = io.BytesIO(fobj.getvalue().encode('utf-8'))

    filename = 'export-{}.csv'.format(int(time.time()))
    return send_file(byteobj,
            attachment_filename=filename,
            as_attachment=True,
            mimetype='text/csv')
