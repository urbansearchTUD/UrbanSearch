import gzip
import io
import json
import logging
import re
import os
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from multiprocessing import Process, cpu_count

import config
from urbansearch.utils import process_utils
logger = logging.getLogger(__name__)


class PageDownloader(object):

    """
    PageDownloader class. Creates object for a downloader with functions
    to download pages for a certain url. Also contains functions to parse
    the downloaded data to plain text.
    """

    def __init__(self):
        self.cc_data_prefix = config.get('gathering', 'cc_data')
        self.cc_index_url = config.get('gathering', 'cc_index')
        self.indices = []
        # Cache the regular expression to filter http response code
        re.compile('\'status\': \'(\w+)\',')

    def download_indices(self, url, collection):
        """
        Download indices corresponding to url from Common Crawl collection.
        Store indices in this PageDownloader object.

        :param url: The url in string format
        :param collection: Name of the collection, e.g CC-Main-2015-27-index
        """
        self._check_url_and_collection(url, collection)

        enc_url = quote(url, safe='')
        try:
            req_timeout = config.get('gathering', 'request_timeout')
            response = requests.get(self.cc_index_url + collection +
                                    '?url=' + enc_url +
                                    '&output=json', timeout=req_timeout)
            indices = [json.loads(x) for x in
                       response.content.strip().descode('utf-8').split('\n')
                       if self._useful_str_responsecode(x)]
            self.indices += indices

        except requests.exceptions.ReadTimeout:
            logger.warning("URL index request timed out")
            # Catch these read exceptions in main application, or increase
            # the timeout value if deemed necessary
            raise

    @staticmethod
    def _check_url_and_collection(url, collection):
        """
        :param url: The url in string format
        :param collection: Name of the collection, e.g CC-Main-2015-27-index
        """
        if not url or not collection:
            logger.warn('Invalid url/collection passed: {0} {1}'.format(
                url, collection))
            raise ValueError('A valid url to query on and an index '
                             'collection must be specified.')

    def download_warc_part(self, index):
        """
        Download the part of the warc file from common crawl servers
        using the JSON index.

        :param index: index in JSON format
        :return: Uncompressed part of warc file if responsecode for index is
        200, otherwise None
        """
        if not index:
            return None

        req_timeout = config.get('gathering', 'request_timeout')
        start, length = int(index['offset']), int(index['length'])
        end = start + length - 1
        try:
            response = requests.get(self.cc_data_prefix + index['filename'],
                                    headers={
                                        'Range': 'bytes={}-{}'.format(start,
                                                                      end)},
                                    timeout=req_timeout)
        except requests.exceptions.RequestException as e:
            logger.warning("Exception while downloading warc part: {0}"
                           .format(e))
            return None

        # Response is compressed gz data, uncompress this using gzip
        data = self._uncompress_gz(response)

        return data

    @staticmethod
    def _uncompress_gz(response):
        compressed_gz = io.BytesIO(response.content)
        with gzip.GzipFile(fileobj=compressed_gz) as gz_obj:
            data = gz_obj.read()
        return data

    @staticmethod
    def _useful_responsecode(index):
        # Check responsecode of index to determine if it's useful to download
        # the part. HTTP 200 is useful, other than 200 will be discarded.

        if index is not None and 'status' in index:
            return int(index['status']) == 200
        else:
            return False

    @staticmethod
    def _useful_str_responsecode(string):
        if not string:
            return False

        # None if no match is found
        status_code = re.search('\"status\": \"(\w+)\",', string)
        return status_code and int(status_code.group(1)) == 200

    def _clean_indices(self, indices):
        # Removes useless entries with status code other than 200
        for index in indices:
            if not self._useful_responsecode(index):
                indices.remove(index)

    @staticmethod
    def warc_html_to_text(data):
        """
        Process uncompressed warc to plain text.

        :param data: Uncrompessed bytes of partial warc
        :return: Plain text without warc headers

        """
        if data is None:
            return ''
        index = data.find("<html".encode())

        if index == -1:
            return ''

        # Strip headers
        data = data[index:-1]
        soup = BeautifulSoup(data, 'html.parser')
        # Remove style and script statements
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text()

    def index_to_txt(self, index):
        """
        Extract plain text using JSON index. Downloads WARC parts from
        common crawl servers and parses to plain text.

        :return: Plain text of web page in str format

        """
        data = self.download_warc_part(index)
        return self.warc_html_to_text(data)

    def indices_from_file(self, filename):
        """
        Opens file with filename and parses JSON,
        adds indices in file to this object. Does not work on cdx indices.

        :param filename: Filename of the file to open
        :return: List of parsed JSON indices
        """
        with open(filename, 'r') as f:
            # Remove the garbage before { and parse to json and add to list
            indices = [json.loads('{' + x.split('{', 1)[-1]) for x in
                       f.read().strip().split('\n')
                       if self._useful_str_responsecode(x)]
            self.indices += indices
            return indices

    def indices_from_gz_file(self, filename):
        """
        Open compressed gz file, uncompress and parse JSON entries in file.
        Indices are added to this instance of PageDownloader.

        :param filename: Path to .gz file
        :return: Return list of indices
        """
        with gzip.GzipFile(filename) as gz_obj:
            # Remove the garbage before { and parse to json and add to list
            indices = [json.loads('{' + x.split('{', 1)[-1]) for x in
                       gz_obj.read().decode('utf-8').strip().split('\n')
                       if self._useful_str_responsecode(x)]

            self.indices += indices
            return indices

    @staticmethod
    def _get_file_paths(directory):
        return [_file.path for _file in os.scandir(directory) if _file.is_file()]

    def run_workers(self, no_of_workers, directory, queue, gz=True):
        """ Run workers to process indices from a directory with files
        in parallel. All parsed indices will be added to the queue.

        :no_of_workers: Number of workers that will run
        :directory: Path to directory containing files
        :queue: multiprocessing.Queue where the indices will be added to
        :gz: Files are in .gz format. Default: True.
        :opt: Determine optimal number of workers and ignore no_of_workers
        parameter
        """
        if (no_of_workers==0):
            try:
                no_of_workers = (cpu_count() * 2) + 1
            except NotImplementedError:
                logger.error("Cannot determine number of CPU's,"
                             + "defaulting to 1 worker")
                no_of_workers = 1

        files = self._get_file_paths(directory)

        div_files = process_utils.divide_files(files, no_of_workers)
        workers = [Process(target=self.worker, args=(queue, div_files[i], gz))
                   for i in range(no_of_workers)]

        for worker in workers:
            worker.start()

        # Wait for processes to finish
        for worker in workers:
            worker.join()

    def worker(self, queue, files, gz):
        """
        Worker that will parse indices from files in file list and put the
        results in a Queue. Can use plain text files containing indices or
        .gz files containing indices.

        :queue: multiprocessing.JoinableQueue to put results in
        :files: List of filepaths to files that this worker will use
        :gz: Use .gz files or not, default: True.
        """
        if gz:
            self._gz_workers(queue, files)
        else:
            self._file_workers(queue, files)

    def _gz_workers(self, queue, files):
        for file in files:
            if file.endswith('.gz'):
                for index in self._worker_indices_from_gz_file(file):
                    queue.put(index)

    def _file_workers(self, queue, files):
        for file in files:
            for index in self.indices_from_file(file):
                queue.put(index)


    def _worker_indices_from_gz_file(self, filename):
        with gzip.GzipFile(filename) as gz_obj:
            # Remove the garbage before { and parse to json and add to list
            # TODO Strip JSON to minimal information
            indices = []
            try:
                indices = [json.loads(x) for x in
                           gz_obj.read().decode('utf-8').strip().split('\n')
                           if self._useful_str_responsecode(x)]
            except OSError as e:
                logger.error("File {0} failed to read: {1}".format(filename,
                                                                   e))
            return indices
