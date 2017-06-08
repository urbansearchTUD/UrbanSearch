import config
from flask import Blueprint, jsonify, request

from urbansearch.server.decorators import is_json
from urbansearch.clustering.classifytext import ClassifyText

predict_api = Blueprint('predict_api', __name__)
ct = ClassifyText()


@predict_api.route('/', methods=['POST'], strict_slashes=False)
@predict_api.route('/predict', methods=['POST'], strict_slashes=False)
@is_json
def predict():
    """
    API route for predicting the category of the supplied text. The request should
    have type set to application/json and the provided JSON
    should have a text attribute containing the text for which we want to
    predict the category.
    """
    try:
        prediction = ct.predict(request.json['document'])

        return jsonify(category=str(prediction[0]),
                       status=200)
    except Exception as e:
        return jsonify(error=True,
                       status=500,
                       message='Getting the prediction failed')


@predict_api.route('/probabilities', methods=['POST'], strict_slashes=False)
@is_json
def probabilities():
    """
    API route for getting the probabilities per category of the supplied text.
    The request should have type set to application/json and the provided JSON
    should have a text attribute containing the text for which we want to
    get the probabilities per category
    """
    try:
        probabilities = ct.probability_per_category(request.json['document'])

        return jsonify(probabilities=probabilities,
                       status=200)
    except:
        return jsonify(error=True,
                       status=500,
                       message='Getting the probabilities failed')
