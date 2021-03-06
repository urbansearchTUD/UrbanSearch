import config
from datetime import datetime
from flask import Blueprint, jsonify, request
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from urbansearch.utils.dataset_p_utils import DatasetPickleUtils
from urbansearch.clustering.binary_modelmanager import BinaryModelManager
from urbansearch.clustering.sgdc_modelmanager import SGDCModelManager

DEFAULT_CLASSIFIER = config.get('classification', 'default_classifier')

classifier_api = Blueprint('classifier_api', __name__)
dpu = DatasetPickleUtils()
smm = SGDCModelManager()


@classifier_api.route('/train', methods=['POST'])
def train():
    if request.args.get('equal') == 'true':
        dataset_path = dpu.generate_equal_dataset()
    else:
        dataset_path = dpu.generate_dataset()

    dataset = dpu.load(dataset_path)

    mm = SGDCModelManager()
    mm.x_train = dataset['inputs']
    mm.y_train = dataset['outputs']

    mm.train()

    if request.args.get('default') == 'true':
        filename = DEFAULT_CLASSIFIER
    else:
        filename = 'clf.{}.pickle'.format(datetime.now().strftime('%d%m%Y'))

    if request.args.get('save') == 'true':
        mm.save(filename)

    return jsonify(status=200, message='success')

@classifier_api.route('/train_equal', methods=['POST'])
def train_equal():
    dataset_path = dpu.generate_equal_dataset()
    dataset = dpu.load(dataset_path)
    mm = SGDCModelManager()

    mm.x_train = dataset['inputs']
    mm.y_train = dataset['outputs']

    mm.train()

    if request.args.get('default') == 'true':
        filename = DEFAULT_CLASSIFIER
    else:
        filename = 'clf.{}.pickle'.format(datetime.now().strftime('%d%m%Y'))

    if request.args.get('save') == 'true':
        mm.save(filename)

    return jsonify(status=200, message='success')

@classifier_api.route('/train_test_equal', methods=['POST'])
def train_test_equal():
    dataset_path = dpu.generate_equal_dataset()
    dataset = dpu.load(dataset_path)
    mm = SGDCModelManager()

    mm.x_train, mm.x_test, mm.y_train, mm.y_test = train_test_split(dataset['inputs'], dataset['outputs'], random_state=42)
    mm.train()
    score = mm.score()

    probabilities = mm.predict(mm.x_test)
    print(mm.score())
    print(classification_report(mm.y_test, probabilities))

    return jsonify(status=200, score=score)


@classifier_api.route('/metrics_equal', methods=['GET'])
def metrics_equal():
    dataset_path = dpu.generate_equal_dataset()
    dataset = dpu.load(dataset_path)
    mm = SGDCModelManager()

    mm.x_train, mm.x_test, mm.y_train, mm.y_test = train_test_split(dataset['inputs'], dataset['outputs'], random_state=42)
    mm.train()
    predicts = mm.predict(mm.x_test)

    report = classification_report(mm.y_test, predicts)

    return jsonify(status=200, message=report)


@classifier_api.route('/probabilities_equal', methods=['GET'])
def probabilities_equal():
    dataset_path = dpu.generate_equal_dataset()
    dataset = dpu.load(dataset_path)
    mm = SGDCModelManager()

    mm.x_train, mm.x_test, mm.y_train, mm.y_test = train_test_split(dataset['inputs'], dataset['outputs'], random_state=42)
    mm.train()
    probabilities = mm.probabilities(mm.x_test)

    result = []
    for i in range(len(mm.y_test)):
        result.append({
            'probabilities': list(probabilities[i]),
            'category': mm.y_test[i]
        })

    return jsonify(status=200, result=result)

@classifier_api.route('/probabilities/binary', methods=['GET'])
def probabilities_binary():
    dataset_path = dpu.generate_equal_dataset()
    dataset = dpu.load(dataset_path)
    mm = BinaryModelManager()

    mm.x_train, mm.x_test, mm.y_train, mm.y_test = train_test_split(dataset['inputs'], dataset['outputs'], random_state=42)
    mm.train()
    probabilities = mm.predict(mm.x_test)

    result = mm.score()
    return jsonify(status=200, result=result)
