import sys
import gzip
import timeit
import os
import logging

from multiprocessing import Lock, Value
from ctypes import c_int

counter = Value(c_int)  # defaults to 0
counter_lock = Lock()

LOGGER = logging.getLogger(__name__)


def _total_index_count(directory):
    # Count total indices of gz files
    lines = 0

    files = [_file.path for _file in os.scandir(directory)
             if _file.is_file()]

    for file in files:
        if file.endswith('.gz'):
            with gzip.GzipFile(file) as gz_obj:
                for l in gz_obj.read().decode('utf-8').split('\n'):
                    lines += 1
    return lines


def _total_file_count(directory):
    # Count total files in directory
    files = 0
    try:
        for _file in os.scandir(directory):
            if _file.is_file():
                files += 1
    except OSError as e:
        LOGGER.error("Counting total files failed with: {0}".format(e))
        return 0
    return files


def print_progress(directory, pre_downloaded=False):
    if pre_downloaded:
        total = _total_file_count(directory)
    else:
        total = _total_index_count(directory)

    start = 0
    been = False

    while counter.value < total:
        if counter.value == 1:
            start = timeit.default_timer()
        if counter.value % 100 == 0 and not been:
            stop = timeit.default_timer()
            avg = (stop - start) / 100
            remaining = (total - counter.value) * avg
            m, s = divmod(remaining, 60)
            h, m = divmod(m, 60)

            sys.stdout.flush()
            sys.stdout.write('Progress: {0}/{1} Left: {2} h {3} m {4} s \r'
                             .format(counter.value, total, h, m, round(s)))
            sys.stdout.flush()
            start = timeit.default_timer()
            been = True
        if counter.value % 100 != 0:
            been = False
