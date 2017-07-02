from flask import Blueprint, jsonify, request

from urbansearch.utils import db_utils

relations_api = Blueprint('relations_api', __name__)


@relations_api.route('/document_info', methods=['GET'], strict_slashes=False)
def all_for_ic_rel():
    if 'city_a' not in request.args or 'city_b' not in request.args:
        return jsonify(status=400, error='No city pair given')

    city_a = request.args.get('city_a')
    city_b = request.args.get('city_b')
    documents = db_utils.get_related_documents(city_a, city_b, int(request.args.get('limit', 300)))

    return jsonify(status=200, documents=documents)


@relations_api.route('/all', methods=['GET'], strict_slashes=False)
def all():
    threshold = int(request.args.get('threshold', 125))
    relations = db_utils.get_ic_rels(None, threshold)

    return jsonify(status=200, relations=relations)
