import config
import os
import pickle
import pytest

from urbansearch.utils import p_utils

TEST_RESOURCES = config.get('resources', 'test')

def test_load():
    pu = p_utils.PickleUtils()
    filename = os.path.join(TEST_RESOURCES, 'test.pickle')
    expected_data = {
        'test': 'string'
    }

    with open(filename, 'wb') as f:
        pickle.dump(expected_data, f, pickle.HIGHEST_PROTOCOL)

    data = pu.load(filename)

    assert os.path.exists(filename)
    assert expected_data['test'] == data['test']

    # Cleanup
    os.remove(filename)

def test_load_no_such_file():
    with pytest.raises(Exception):
        pu = p_utils.PickleUtils()
        pu.load('non_existing_filename')

def test_save():
    pu = p_utils.PickleUtils()
    filename = os.path.join(TEST_RESOURCES, 'test.pickle')
    data = {
        'test': 'string'
    }

    pu.save(data, filename)
    assert os.path.exists(filename)

    with open(filename, 'rb') as f:
        loaded_data = pickle.load(f)

    assert data['test'] == loaded_data['test']

    # Cleanup
    os.remove(filename)

def test_save_no_such_file():
    with pytest.raises(Exception):
        pu = p_utils.PickleUtils()
        pu.save({}, 'non/existing/filename')
