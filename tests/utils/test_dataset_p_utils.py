import config
import datetime
import os
import pickle
import pytest

from urbansearch.utils import dataset_p_utils, p_utils

DATA_SETS_DIRECTORY = config.get('resources', 'data_sets')

dataset_list = {
    'inputs': [
        'dsf sdfsdaf sadfsdafaf',
        'sdfsdfsdfsdafsd'
    ],
    'output': ''
}

dataset_no_list = {
    'inputs': '',
    'output': ''
}
pdu = dataset_p_utils.DatasetPickleUtils()
pu = p_utils.PickleUtils()

def test_load():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    pu.save(dataset_list, file_path)
    data = pdu.load(filename)

    assert data['output'] == dataset_list['output']
    for i,d in enumerate(data['inputs']):
        assert d == dataset_list['inputs'][i]

    os.remove(file_path)

def test_save():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    pdu.save({}, filename)
    assert os.path.exists(file_path)
    os.remove(file_path)

def test_append_to_inputs():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    pdu.save(dataset_list, filename)

    pdu.append_to_inputs('yolo nolo', filename=filename)

    data = pdu.load(filename)
    assert len(data['inputs']) == 3
    assert 'yolo nolo' in data['inputs']

    os.remove(file_path)

def test_append_to_inputs_no_list():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    with pytest.raises(Exception):
        pdu.save(dataset_no_list, filename)
        pdu.append_to_inputs('yolo nolo', filename=filename)

    os.remove(file_path)

def test_append_list_to_inputs():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    pdu.save(dataset_list, filename)

    pdu.append_list_to_inputs(['yolo nolo', 'nolo yolo'], filename=filename)

    data = pdu.load(filename)
    assert len(data['inputs']) == 4
    assert 'yolo nolo' in data['inputs']
    assert 'nolo yolo' in data['inputs']

    os.remove(file_path)

def test_append_no_list_to_inputs():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)
    pdu.save(dataset_list, filename)

    with pytest.raises(Exception):
        pdu.append_list_to_inputs('yolo nolo', filename=filename)

    os.remove(file_path)

def test_append_list_to_inputs_no_list():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)
    pdu.save(dataset_no_list, filename)

    with pytest.raises(Exception):
        pdu.append_list_to_inputs(['yolo nolo', 'nolo yolo'], filename=filename)

    os.remove(file_path)

def test_category_to_file():
    assert pdu._category_to_file('education') == 'education.pickle'

def test_filename_to_path():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)
    assert file_path == pdu._filename_to_path(filename)

def test_init_categoryset():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    pdu.init_categoryset('test_123',
                         inputs=['bla', 'blabla'])

    data = pdu.load(filename)

    assert data['output'] == 'test_123'
    assert len(data['inputs']) == 2

    pdu.init_categoryset('test_123',
                         inputs='test')

    data = pdu.load(filename)

    assert data['output'] == 'test_123'
    assert len(data['inputs']) == 0

    pdu.init_categoryset('test_123')

    data = pdu.load(filename)

    assert data['output'] == 'test_123'
    assert len(data['inputs']) == 0

    os.remove(file_path)

def test_init_dataset():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    pdu.init_dataset(filename, outputs=['test', 'test2'],
                         inputs=['bla', 'blabla'])

    data = pdu.load(filename)

    assert len(data['outputs']) == 2
    assert len(data['inputs']) == 2

    pdu.init_dataset(filename, outputs=['test'],
                         inputs='test')

    data = pdu.load(filename)

    assert len(data['outputs']) == 0
    assert len(data['inputs']) == 0

    pdu.init_dataset(filename)

    data = pdu.load(filename)

    assert len(data['outputs']) == 0
    assert len(data['inputs']) == 0

    os.remove(file_path)

def test_generate_dataset():
    i = datetime.datetime.now()
    expected_filename = 'data.{}.pickle'.format(i.strftime('%d%m%Y'))
    expected_file_path = os.path.join(DATA_SETS_DIRECTORY, expected_filename)

    education_filename = 'education.pickle'
    education_file_path = os.path.join(DATA_SETS_DIRECTORY, education_filename)
    pdu.init_categoryset('education', inputs=['test'])

    commuting_filename = 'commuting.pickle'
    commuting_file_path = os.path.join(DATA_SETS_DIRECTORY, commuting_filename)
    pdu.init_categoryset('commuting', inputs=['test'])

    pdu.generate_dataset()

    data = pdu.load(expected_filename)

    assert len(data['inputs']) == 2
    assert len(data['outputs']) == 2

    os.remove(commuting_file_path)
    os.remove(education_file_path)
    os.remove(expected_file_path)


def test_set_output():
    filename = 'test_123.pickle'
    file_path = os.path.join(DATA_SETS_DIRECTORY, filename)

    pdu.init_categoryset('test_123',
                         inputs=['bla', 'blabla'])

    pdu.set_output(filename, 'yolo')

    data = pdu.load(filename)
    assert data['output'] == 'yolo'
