import gzip
import timeit
import os
import logging
import curses  # Unix only..
import statistics

from multiprocessing import Lock, Value
from ctypes import c_int

counter = Value(c_int)  # defaults to 0
ind_counter = Value(c_int)

ind_counter_lock = Lock()
counter_lock = Lock()

console = curses.initscr()
curses.noecho()
curses.cbreak()

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


def _curses_print(current, total, time, ind_time, indices_progress=False):
    if time is not None:
        h, m, s = time
    h_i, m_i, s_i = ind_time
    if time is not None:
        console.addstr(0, 0, 'Progress: {0}/{1} Left: {2} h {3} m {4} s \r'
                       .format(current, total, h, m, s))
        if indices_progress:
            console.addstr(1, 0, 'Indices Progress: {0}/{1} Left: {2} h {3} m {4} s\r'
                           .format(ind_counter.value, total, h_i, m_i, s_i))
    console.refresh()


def print_progress(directory, pre_downloaded=False, indices_progress=False):
    if pre_downloaded:
        total = _total_file_count(directory)
    else:
        total = _total_index_count(directory)

    start = 0
    ind_start = 0
    ind_stop = 0
    h, m, s, h2, m2, s2 = (999,) * 6
    been = False
    avg_lst = list()
    avg_index = 0
    ind_avg_lst = list()
    ind_avg_index = 0

    while counter.value < total:
        if counter.value == 1:
            start = timeit.default_timer()
        if ind_counter.value == 1:
            ind_start = timeit.default_timer()
        if counter.value % 100 == 0 and counter.value > 0:
            stop = timeit.default_timer()
            avg = (stop - start) / 100
            if avg_index >= 100:
                avg_index = 0
            avg_lst.insert(avg_index, avg)
            avg_index += 1
            final_avg = statistics.median(avg_lst)
            remaining = (total - counter.value) * avg
            m, s = divmod(remaining, 60)
            h, m = divmod(m, 60)

            _curses_print(counter.value, total, (h, m, round(s)), (h2, m2, s2),
                          indices_progress=indices_progress)
            start = timeit.default_timer()

        if indices_progress:
            if ind_counter.value % 50 == 0 and not been:
                ind_stop = timeit.default_timer()
                ind_avg = (ind_stop - ind_start) / 50
                if ind_avg_index >= 100:
                    ind_avg_index = 0
                ind_avg_lst.insert(ind_avg_index, ind_avg)
                ind_avg_index += 1
                final_avg = statistics.median(ind_avg_lst)
                ind_remaining = (total - ind_counter.value) * final_avg
                m2, s2 = divmod(ind_remaining, 60)
                h2, m2 = divmod(m2, 60)
                _curses_print(counter.value, total, None, (h2, m2, round(s2)),
                              indices_progress=True)
                ind_start = timeit.default_timer()
                been = True
            elif ind_counter.value % 50 != 0:
                been = False

    _print_progress_cleanup()


def _print_progress_cleanup():
    curses.echo()
    curses.nocbreak()
    curses.endwin()
