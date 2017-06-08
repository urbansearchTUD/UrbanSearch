import config
from flask import Blueprint, jsonify, request

from urbansearch.server.decorators import is_json
from urbansearch.utils.dataset_p_utils import DatasetPickleUtils

dataset_api = Blueprint('dataset_api', __name__)
dpu = DatasetPickleUtils()


@dataset_api.route('/append', methods=['POST'], strict_slashes=False)
@is_json
def append():
    """
    Append the document supplied in the body of the request to the categoryset.
    """
    try:
        data = request.json
        dpu.append_to_inputs(data['document'], category=data['category'])
        return jsonify(status=200,
                       message='Document successfully added')
    except Exception as e:
        return jsonify(error=True,
                       status=400,
                       message='Invalid JSON supplied for this API call')


@dataset_api.route('/create', methods=['GET'], strict_slashes=False)
def create():
    """
    Create a dataset from all the available category sets
    """
    try:
        dpu.generate_dataset()
        return jsonify(status=200,
                       message='Dataset successfully created')
    except Exception as e:
        return jsonify(error=True,
                       status=500,
                       message='Creation of dataset failed')


@dataset_api.route('/create/categoryset', methods=['POST'], strict_slashes=False)
@is_json
def create_categoryset():
    """
    Create a categoryset for the supplied category. The category should be
    specified in the body of the request. Also a list of documents should
    be included in the body of the request, the list can be empty.
    """
    try:
        data = request.json
        dpu.init_categoryset(data['category'], inputs=data['documents'])

        return jsonify(status=200,
                       message='Categoryset successfully created')
    except Exception as e:
        return jsonify(error=True,
                       status=500,
                       message='Creation of categoryset failed')
