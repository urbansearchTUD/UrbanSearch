from flask import Blueprint, jsonify

from urbansearch.utils import db_utils

cities_api = Blueprint('cities_api', __name__)


@cities_api.route('/all', methods=['GET'], strict_slashes=False)
def all():
    return jsonify(status=200, cities=db_utils.cities())
