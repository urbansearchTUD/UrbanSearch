import gzip
import io
import json
import logging
import re
import os
import requests

from urllib.parse import quote
from bs4 import BeautifulSoup
from multiprocessing import Process
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import config
from urbansearch.utils import process_utils

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
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
        self.req_timeout = config.get('gathering', 'request_timeout')
        self.session = requests.Session()

        # Cache the regular expression to filter http response code
        re.compile('\'status\': \'(\w+)\',')

    def download_indices(self, url, collection):
        """
        Download indices corresponding to url from Common Crawl collection.
        Store indices in this PageDownloader object.

        :param url: The url in string format
        :param collection: Name of the collection, e.g CC-Main-2015-27-index
        """
        if not url or not collection:
            logger.warn('Invalid url/collection passed: {0} {1}'.format(
                url, collection))
            raise ValueError('A valid url to query on and an index '
                             'collection must be specified.')

        enc_url = quote(url, safe='')
        try:
            response = self.session.get(self.cc_index_url + collection +
                                        '?url=' + enc_url +
                                        '&output=json',
                                        timeout=self.req_timeout)

            indices = [json.loads(x) for x in
                       response.content.strip().decode('utf-8').split('\n')
                       if self._useful_str_responsecode(x)]
            self.indices += indices

        except requests.exceptions.ReadTimeout:
            logger.warning('URL index request timed out')
            # Catch these read exceptions in main application, or increase
            # the timeout value if deemed necessary
            raise

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

        start, length = int(index['offset']), int(index['length'])
        end = start + length - 1
        try:
            resp = self.session.get(self.cc_data_prefix + index['filename'],
                                    headers={
                                        'Range': 'bytes={}-{}'.format(start,
                                                                      end)},

                                    timeout=self.req_timeout, verify=False)
        except requests.exceptions.RequestException as e:
            logger.warning('Exception while downloading warc part: {0}'
                           .format(e))
            return None

        # Response is compressed gz data, uncompress this using gzip
        data = self._uncompress_gz(resp)

        return data

    @staticmethod
    def _uncompress_gz(response):
        try:
            compressed_gz = io.BytesIO(response.content)
            with gzip.GzipFile(fileobj=compressed_gz) as gz_obj:
                data = gz_obj.read()
        except OSError as e:
            logger.error("Uncompressing gz file failed with error: {0}"
                         .format(e))
            data = None
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
        for script in soup(['script', 'style']):
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

    def index_to_raw_text(self, index):
        """
        Extract plain text using JSON index. Downloads WARC parts from
        common crawl servers and parses to raw utf-8 text. Contains html
        and other headers.

        :return: Raw text of web page in str format

        """
        data = self.download_warc_part(index)
        return data.decode('utf-8')

    def indices_from_file(self, filename):
        """
        Opens file with filename and parses JSON,
        adds indices in file to this object. Does not work on cdx indices.

        :param filename: Filename of the file to open
        :return: List of parsed JSON indices
        """
        with open(filename, 'r', errors='replace') as f:
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

    def run_workers(self, num_workers, directory, queue, **kwargs):
        """ Run workers to process indices from a directory with files
        in parallel. All parsed indices will be added to the queue.

        :num_workers: Number of workers that will run
        :directory: Path to directory containing files
        :queue: multiprocessing.Queue where the indices will be added to
        :gz: Passed in kwargs. Files are in .gz format. Default: True
        :opt: Passed in kwargs. Determine optimal number of workers and
        ignore num_workers parameter
        """
        if kwargs.get('opt'):
            num_workers = process_utils.compute_num_workers()

        files = [_file.path for _file in os.scandir(directory)
                 if _file.is_file()]

        div_files = process_utils.divide_files(files, num_workers)
        workers = [Process(target=self.worker, args=(queue, div_files[i],
                                                     kwargs.get('gz', True)))
                   for i in range(num_workers)]

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
            for file in files:
                if file.endswith('.gz'):
                    for index in self._worker_indices_from_gz_file(file):
                        queue.put(index)
        else:
            for file in files:
                for index in self.indices_from_file(file):
                    queue.put(index)

    def _worker_indices_from_gz_file(self, filename):
        with gzip.GzipFile(filename) as gz_obj:
            indices = []
            try:
                # Strips JSON to minimal information (length, offset & name)
                indices = [json.loads(x, object_hook=self._remove_keys)
                           for x in
                           gz_obj.read().decode('utf-8').strip().split('\n')
                           if self._useful_str_responsecode(x)]
            except OSError as e:
                logger.error('File {0} failed to read: {1}'.format(filename,
                                                                   e))
            return indices

    @staticmethod
    def _remove_keys(json_dict):
        # Strip all key-value pairs other than digest, length, offset & name
        return {k: v for k, v in json_dict.items()
                if k in ['digest', 'length', 'offset', 'filename']}
