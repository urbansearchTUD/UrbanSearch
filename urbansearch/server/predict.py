import config
from flask import Blueprint, jsonify

from urbansearch.clustering.classifytext import ClassifyText

predict_api = Blueprint('predict_api', __name__)
ct = ClassifyText()

@predict_api.route('/classify', methods=['POST', 'GET'])
@predict_api.route('/classify/predict', methods=['POST', 'GET'])
def predict():
    """
    API route for predicting the category of the supplied text. Or returning a
    info page if method is GET. The request should have type set to
    application/json and the provided JSON should have a text attribute
    containing the text for which we want to predict the category
    """

    if request.method == 'GET':
        # TODO: render info page
        pass
    elif request.method == 'POST' and request.is_json():
        data = request.json()
        prediction = ct.predict(data['text'])
        return jsonify(result=prediction,
                       status='200')

@predict_api.route('/classify/probabilities')
def probabilities():
    """
    API route for getting the probabilities per category of the supplied text.
    Or returning a info page if method is GET.
    The request should have type set to application/json and the provided JSON
    should have a text attribute containing the text for which we want to
    get the probabilities per category
    """
    if request.method == 'GET':
        # TODO: render info page
        pass
    elif request.method == 'POST' and request.is_json():
        data = request.json()
        prediction = ct.probability_per_category(data['text'])
        return jsonify(result=prediction,
                       status='200')
