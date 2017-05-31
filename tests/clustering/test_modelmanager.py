import config
import os
import pickle
from numpy import ndarray
from sklearn.pipeline import Pipeline
from unittest.mock import patch

from urbansearch.clustering import modelmanager

TEST_FILENAME = 'test_file.pickle'
MODELS_DIRECTORY = config.get('resources', 'models')
TEST_SETS_DIRECTORY = config.get('resources', 'test_sets')
TRAINING_SETS_DIRECTORY = config.get('resources', 'training_sets')
VALIDATION_SETS_DIRECTORY = config.get('resources', 'validation_sets')

def test_init_no_file():
    mm = modelmanager.ModelManager()
    assert mm.clf == None

def test_init():
    mm = modelmanager.ModelManager(filename='sgdcmodel.pickle')
    assert mm.clf != None
    assert isinstance(mm.clf, Pipeline)

def test_load(filename='sgdcmodel.pickle'):
    mm = modelmanager.ModelManager()
    assert mm.clf == None
    mm.clf = mm.load('sgdcmodel.pickle')
    assert isinstance(mm.clf, Pipeline)

@patch.object(pickle, 'load')
def test_load_trainingset(mock_method):
    mm = modelmanager.ModelManager()
    mm.load_trainingset(TEST_FILENAME)
    assert mock_method.call_count == 1

@patch.object(pickle, 'load')
def test_load_testset(mock_method):
    mm = modelmanager.ModelManager()
    mm.load_testset(TEST_FILENAME)
    assert mock_method.call_count == 1

@patch.object(pickle, 'load')
def test_load_validationset(mock_method):
    mm = modelmanager.ModelManager()
    mm.load_validationset(TEST_FILENAME)
    assert mock_method.call_count == 1

def test_predict():
    mm = modelmanager.ModelManager(filename='sgdcmodel.pickle')
    prediction = mm.predict(['ssdfsaf dsfsadfds dsfsdafsd'])
    assert prediction
    assert isinstance(prediction[0], str)

def test_predict_no_clf():
    mm = modelmanager.ModelManager()
    prediction = mm.predict(['ssdfsaf dsfsadfds dsfsdafsd'])
    assert prediction == None

def test_propabilities():
    mm = modelmanager.ModelManager(filename='sgdcmodel.pickle')
    prediction = mm.probabilities(['ssdfsaf dsfsadfds dsfsdafsd'])
    assert prediction != None
    assert isinstance(prediction[0], ndarray)

def test_propabilities_no_clf():
    mm = modelmanager.ModelManager()
    prediction = mm.probabilities(['ssdfsaf dsfsadfds dsfsdafsd'])
    assert prediction == None

@patch.object(pickle, 'dump')
def test_save_no_clf(mock_method):
    mm = modelmanager.ModelManager()
    mm.save(TEST_FILENAME)
    assert mock_method.call_count == 0

@patch.object(pickle, 'dump')
def test_save(mock_method):
    mm = modelmanager.ModelManager(filename='sgdcmodel.pickle')
    mm.save(TEST_FILENAME)
    assert mock_method.call_count == 1
