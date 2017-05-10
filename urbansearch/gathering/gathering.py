import gzip
import json
import requests
import io
from bs4 import BeautifulSoup
from urllib.parse import quote


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
        response = requests.get(self.cc_index_url + collection +
                                '?url=' + enc_url + '&output=json')
        print(response.content)
        indices = [json.loads(x) for x in
                   response.content.strip().decode('utf-8').split('\n')]
        self.indices += indices
    
    def download_warc_part(self, index):
        """
        Download the part of the warc file using the JSON index.
        
        :param index: index in JSON format
        :return: Uncompressed part of warc file
        """
        start, length = int(index['offset']), int(index['length'])
        end = start + length - 1
        response = requests.get(self.cc_data_prefix + index['filename'],
                                headers={'Range': 'bytes={}-{}'.format(start, end)})
        
        # Response is compressed gz data, uncompress this using gzip
        compressed_gz = io.BytesIO(response.content)
        gz_obj = gzip.GzipFile(fileobj=compressed_gz)
        data = gz_obj.read()
        gz_obj.close()
        return data

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
        Extract plain text using JSON index.

        :return: Plain text of web page in str format

        """
        data = self.download_warc_part(index)
        return self.warc_html_to_text(data)

    def indices_from_file(self, filename):
        """
        Opens file with filename and parses JSON,
        adds indices in file to this object.

        :param filename: Filename of the file to open
        :return: List of parsed JSON indices
        """
        with open(filename, 'rb') as f:
            indices = [json.loads(x) for x in
                       f.read().decode('utf-8').strip().split('\n')]
            self.indices += indices
            return indices

# Test code, remove later
pd = PageDownloader()
pd.indices_from_file('/home/gijs/BEP/test_index')
pd.download_indices('http://commoncrawl.org/faqs/', 'CC-MAIN-2015-27-index')
test_data = pd.download_warc_part(pd.indices[0])
print(pd.warc_html_to_text(test_data))

