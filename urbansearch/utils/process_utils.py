import logging
from multiprocessing import cpu_count


logger = logging.getLogger(__name__)


def divide_files(files, parts):
    """ Divide a list of files into parts as equal as possible. Returns a list
    with lists inside corresponding to the number of parts.

    :files: The list with files
    :parts: Number of parts
    :return: List of filelists divided, that have been divided into the
    specified number of parts
    """
    if (not files and parts <= 0) or len(files) <= 0:
        return None
    files_len = len(files)
    if parts > files_len:
        part_len = 1
    else:
        part_len = files_len // parts
    # Divide all files in 'equal' parts
    div_files = [files[i * part_len:part_len * (i + 1)]
                 for i in range(parts)]

    # If number of data entries is odd, append last file to last list
    if files_len % 2 != 0:
        div_files[-1] += [files[-1]]

    return div_files


def compute_num_workers():
    """
    Computes the number of workers for gathering documents.
    :return: The number of CPU's * 2 + 1 or 1 if the number of CPU's cannot
    be determined.
    """
    try:
        return cpu_count() * 2 + 1
    except NotImplementedError:
        logger.error('Cannot determine number of CPU\'s, defaulting to 1 '
                     'worker')
        return 1
