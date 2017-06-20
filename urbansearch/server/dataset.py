import config
from flask import Blueprint, jsonify, request

from urbansearch.server.decorators import is_json
from urbansearch.utils.dataset_p_utils import DatasetPickleUtils

CATEGORIES = config.get('score', 'categories')

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

        return jsonify(status=200, message='Document successfully added')
    except:
        return jsonify(error=True, status=400,
                       message='Invalid JSON supplied for this API call')

@dataset_api.route('/append_all', methods=['POST'], strict_slashes=False)
@is_json
def append_all():
    """
    Append the document supplied in the body of the
    request to the categorysets.
    """
    try:
        data = request.json
        for category in data['categories']:
            dpu.append_to_inputs(data['document'], category=category)

        return jsonify(status=200, message='Document successfully added')
    except:
        return jsonify(error=True, status=400,
                       message='Invalid JSON supplied for this API call')


@dataset_api.route('/create', methods=['GET'], strict_slashes=False)
def create():
    """
    Create a dataset from all the available category sets
    """
    try:
        dpu.generate_dataset()

        return jsonify(status=200, message='Dataset successfully created')
    except:
        return jsonify(error=True, status=500,
                       message='Creation of dataset failed')


@dataset_api.route('/create/categoryset', methods=['POST'],
                   strict_slashes=False)
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

        return jsonify(status=200, message='Categoryset successfully created')
    except:
        return jsonify(error=True, status=500,
                       message='Creation of categoryset failed')


@dataset_api.route('/init_categorysets', methods=['POST'],
                   strict_slashes=False)
def init_categorysets():
    try:
        dpu.init_categorysets()
        return jsonify(status=200,
                       message='Categorysets initialized successfully')
    except:
        return jsonify(error=True, status=500,
                       message='Initialization of categorysets failed')

@dataset_api.route('/lengths', methods=['GET'],
                   strict_slashes=False)
def lengths():
    """
    Returns the length of each category dataset
    """
    try:
        lengths = {}

        for category in CATEGORIES:
            data = dpu.load('{}.pickle'.format(category))
            lengths[category] = len(data['inputs'])

        return jsonify(status=200,
                       lengths=str(lengths))
    except:
        return jsonify(error=True, status=500,
                       message='Initialization of categorysets failed')


@dataset_api.route('/persist/categorysets', methods=['POST'],
                   strict_slashes=False)
def persist_categorysets():
    """
    Persist the current categorysets
    """
    try:
        dpu.persist_categorysets()
        return jsonify(status=200, message='Categorysets successfully saved')
    except Exception as e:
        print(e)
        return jsonify(error=True, status=500,
                       message='Save of categorysets failed')
