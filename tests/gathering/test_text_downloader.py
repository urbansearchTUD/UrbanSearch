import os

import config
from urbansearch.gathering import text_downloader


def test_worker(tmpdir):
    td = text_downloader.TextDownloader()
    _file = os.path.join(config.get('resources', 'test'), 'relevant.gz')

    with open(os.path.join(config.get('resources', 'test'),
                           'W0-0.txt'), "r") as text_file:
        exp = text_file.readlines()

    td.worker([_file], str(tmpdir), 0)
    with open(os.path.join(str(tmpdir), 'W0-0.txt'), 'r') as f:
            assert f.readlines()[10] == exp[10]


def test_write_txt_file(tmpdir):
    td = text_downloader.TextDownloader()
    td._write_txt_file_index('a', 'b', str(tmpdir), 123, 456)
    with open(os.path.join(str(tmpdir), 'W123-456.txt'), 'r') as f:
            assert f.readline() == 'a\n'
            assert f.readline() == 'b'


def test_parse_arguments():
    td = text_downloader.TextDownloader()
    in_args = ['dir', '33', 'out']
    args = td._parse_arguments(in_args)
    assert args.directory == 'dir'
    assert args.workers == 33
    assert args.output == 'out'

"""
def test_run_workers(tmpdir):
    td = text_downloader.TextDownloader()
    directory = os.path.join(config.get('resources', 'test'), 'indices_dir/')
    with open(os.path.join(config.get('resources', 'test'),
                           'W1-0.txt'), "r") as text_file:
        exp = text_file.readlines()

    td.run_workers(2, directory, str(tmpdir))
    # Check line in middle of text
    # Could be either Worker1 or Worker 0, so try and except
    _file = next(os.scandir(str(tmpdir)))
    with open(_file.path, 'r') as f:
            assert f.readlines()[1] == exp[1]
"""
