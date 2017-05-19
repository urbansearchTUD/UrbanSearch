import gzip
import io
import json
import logging
import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

import config

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
        enc_url = quote(url, safe='')
        try:
            raise requests.exceptions.ReadTimeout
            req_timeout = config.get('gathering', 'request_timeout')
            response = requests.get(self.cc_index_url + collection +
                                    '?url=' + enc_url +
                                    '&output=json', timeout=req_timeout)
            indices = [json.loads(x) for x in
                       response.content.strip().decode('utf-8').split('\n')
                       if self._useful_str_responsecode(x)]
            self.indices += indices

        except requests.exceptions.ReadTimeout:
            logger.warning("URL index request timed out")
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

        req_timeout = config.get('gathering', 'request_timeout')
        start, length = int(index['offset']), int(index['length'])
        end = start + length - 1
        try:
            response = requests.get(self.cc_data_prefix + index['filename'],
                                    headers={'Range': 'bytes={}-{}'.format(start, end)},
                                    timeout=req_timeout)
        except requests.exceptions.ReadTimeout:
            logger.warning("Timeout while downloading warc part")
            return None

        # Response is compressed gz data, uncompress this using gzip
        compressed_gz = io.BytesIO(response.content)
        with gzip.GzipFile(fileobj=compressed_gz) as gz_obj:
            data = gz_obj.read()

        return data

    @staticmethod
    def _useful_responsecode(index):
        # Check responsecode of index to determine if it's useful to download
        # the part. HTTP 200 is useful, other than 200 will be discarded.

        if index is not None:
            return int(index['status']) == 200
        else:
            return False

    @staticmethod
    def _useful_str_responsecode(string):
        if string:
            return int(re.search('\"status\": \"(\w+)\",', string)
                       .group(1)) == 200

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
