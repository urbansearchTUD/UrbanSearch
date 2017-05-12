import gzip
import json
import requests
import io
from bs4 import BeautifulSoup
from urllib.parse import quote
import config


class PageDownloader(object):

    """
    PageDownloader class. Creates object for a downloader with functions
    to download pages for a certain url. Also contains functions to parse
    the downloaded data to plain text.
    """

    def __init__(self):
        # TODO Put in config?
        self.cc_data_prefix = 'https://commoncrawl.s3.amazonaws.com/'
        self.cc_index_url = 'http://index.commoncrawl.org/'
        self.indices = []

    def download_indices(self, url, collection):
        """
        Download indices corresponding to url from Common Crawl collection.
        Store indices in this PageDownloader object.

        :param url: The url in string format
        :param collection: Name of the collection, e.g CC-Main-2015-27-index
        """
        enc_url = quote(url, safe='')
        try:
            req_timeout = config.get('gathering', 'request_timeout')
            response = requests.get(self.cc_index_url + collection +
                                    '?url=' + enc_url +
                                    '&output=json', timeout=req_timeout)
            print(response.content)
            indices = [json.loads(x) for x in
                       response.content.strip().decode('utf-8').split('\n')]
            # TODO Benchmark to check forward scanning string for status is
            # faster than removing after JSON
            self._clean_indices(indices)
            self.indices += indices

        except requests.exceptions.ReadTimeout:
            print("URL index request timed out")

    def download_warc_part(self, index):
        """
        Download the part of the warc file from common crawl servers
        using the JSON index.

        :param index: index in JSON format
        :return: Uncompressed part of warc file if responsecode for index is
        200, otherwise None
        """
        req_timeout = config.get('gathering', 'request_timeout')
        start, length = int(index['offset']), int(index['length'])
        end = start + length - 1
        try:
            response = requests.get(self.cc_data_prefix + index['filename'],
                                    headers={'Range': 'bytes={}-{}'.format(start, end)}, 
                                    timeout=req_timeout)
        except requests.exceptions.ReadTimeout:
            print("Timeout while downloading warc part")
            return None

        # Response is compressed gz data, uncompress this using gzip
        compressed_gz = io.BytesIO(response.content)
        with gzip.GzipFile(fileobj=compressed_gz) as gz_obj:
            data = gz_obj.read()

        return data

    def _useful_responsecode(self, index):
        # Check responsecode of index to determine if it's useful to download
        # the part. HTTP 200 is useful, other than 200 will be discarded.
        if index:
            return True if int(index['status']) == 200 else False
        return False

    def _clean_indices(self, indices):
        # Removes useless entries with status code other than 200
        for index in indices:
            if not self._useful_responsecode(index):
                indices.remove(index)

    def warc_html_to_text(self, data):
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
        for script in soup(["script", "style"]):
            script.extract()
        plain_txt = soup.get_text()
        return plain_txt

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
                       f.read().strip().split('\n')]
            self._clean_indices(indices)
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
                       gz_obj.read().decode('utf-8').strip().split('\n')]

            self._clean_indices(indices)
            self.indices += indices
            return indices

