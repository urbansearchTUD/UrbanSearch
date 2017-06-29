import time
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
#curses.cbreak()

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
    if ind_time is not None:
        h_i, m_i, s_i = ind_time

    if time is not None:
        console.addstr(0, 0, 'Progress: {0}/{1} Left: {2} h {3} m {4} s \r'
                       .format(current, total, h, m, s))
    if indices_progress and ind_time is not None:
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
    been = False
    avg_history = [0, []]
    avg_ind_history = [0, []]

    while counter.value < total:
        if counter.value == 1:
            start = timeit.default_timer()
        if ind_counter.value == 1:
            ind_start = timeit.default_timer()
        if counter.value % 100 == 0 and counter.value > 0:
            stop = timeit.default_timer()
            avg = (stop - start) / 100

            avg_history, final_avg = _avg_time_spent(avg_history, avg)
            time_left = _time_remaining(total, counter.value, final_avg)
            _curses_print(counter.value, total, time_left, None,
                          indices_progress=indices_progress)
            start = timeit.default_timer()

        if indices_progress:
            if ind_counter.value % 50 == 0 and not been:
                ind_stop = timeit.default_timer()
                ind_avg = (ind_stop - ind_start) / 50
                avg_ind_history, final_avg = _avg_time_spent(avg_ind_history,
                                                             ind_avg)

                ind_time = _time_remaining(total, ind_counter.value, final_avg)
                _curses_print(counter.value, total, None, ind_time,
                              indices_progress=True)
                ind_start = timeit.default_timer()
                been = True
            elif ind_counter.value % 50 != 0:
                been = False
        # Avoid using 100% CPU
        time.sleep(0.01)
    _print_progress_cleanup()


def print_indices_progress(directory):
    total = _total_index_count(directory)

    ind_start = 0
    ind_stop = 0
    been = False
    avg_ind_history = [0, []]

    while ind_counter.value < total:
        if ind_counter.value % 50 == 0 and not been:
            ind_stop = timeit.default_timer()
            ind_avg = (ind_stop - ind_start) / 50
            avg_ind_history, final_avg = _avg_time_spent(avg_ind_history,
                                                         ind_avg)

            ind_time = _time_remaining(total, ind_counter.value, final_avg)
            _curses_print(counter.value, total, None, ind_time,
                          indices_progress=True)
            ind_start = timeit.default_timer()
            been = True
        elif ind_counter.value % 50 != 0:
            been = False
        # Avoid using 100% CPU
        time.sleep(0.01)
    _print_progress_cleanup()


def _avg_time_spent(history, value):
    index = history[0]
    avg_list = history[1]

    if index >= 100:
        index = 0
    avg_list.insert(index, value)
    index += 1
    final_avg = statistics.median(avg_list)

    return [index, avg_list], final_avg


def _time_remaining(total, current, avg):
    remaining = (total - current) * avg
    minutes, seconds = divmod(remaining, 60)
    hours, minutes = divmod(minutes, 60)

    return (hours, minutes, round(seconds))


def _print_progress_cleanup():
    curses.echo()
    curses.nocbreak()
    curses.endwin()
