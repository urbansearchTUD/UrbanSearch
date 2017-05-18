import os
import json

from urbansearch.gathering import indices_selector
import config


def test_irrelevant_indices_from_gz_file():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    _file = os.path.join(config.get('resources', 'test'), 'domain-nl-0000.gz')
    relevant = ind_sel.relevant_indices_from_file(_file)
    assert len(relevant) == 0


def test_relevant_indices_from_gz_file():
    ind_sel = indices_selector.IndicesSelector(cities=['Rotterdam',
                                                       'Wassenaar'])
    _file = os.path.join(config.get('resources', 'test'), 'relevant.gz')
    relevant = ind_sel.relevant_indices_from_file(_file)
    assert len(relevant) == 1


def test_relevant_indices_from_other_file():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    _file = os.path.join(config.get('resources', 'test'), 'indices2.txt')
    relevant = ind_sel.relevant_indices_from_file(_file)
    assert len(relevant) == 1


def test_relevant_indices_from_dir():
    ind_sel = indices_selector.IndicesSelector(cities=['Delft', 'De Bilt'])
    assert len(ind_sel.page_downloader.indices) == 0
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    relevant = ind_sel.relevant_indices_from_dir(directory)
    assert len(relevant) == 1
    assert relevant[0]['digest'] == 'WPTH3FM5VR7UGLA5PZS5L5YI22TNIKXG'