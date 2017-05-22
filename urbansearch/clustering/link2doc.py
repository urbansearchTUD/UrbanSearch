import requests
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> link collector
import time
from bs4 import BeautifulSoup

from .text_preprocessor import PreProcessor

UNWANTED_TAGS = ['head', 'script', 'link', 'meta', 'img', 'style']


class Link2Doc(object):
    """
    A Link2Doc object can fetch and process the contents of a page that is
    requested with the supplied link to the get_doc function
    """

    def __init__(self):
        self.pp = PreProcessor()

    def get_doc(self, link):
        """
        Gets a page and processes it to a string. Unwanted HTML tags get
        stripped by the strip_crap parser.

        :param link: The link to fetch the content from
        :return: String containing the content of the requested page
        """
        try:
            r = requests.get(link)

            if not r.status_code == requests.codes.ok:
                return ''

            soup = BeautifulSoup(r.text, 'html.parser')
            self.strip_unwanted_tags(soup)

            return self.pp.pre_process(soup.get_text())
        except:
            return ''

    def strip_unwanted_tags(self, soup):
        """
        Strips the unwanted tags from a HTML document.

        :param soup: A BeautifulSoup object to clean
        :return: Cleaned soup object
        """
        [e.decompose() for e in soup.findAll(UNWANTED_TAGS)]
=======
from bs4 import BeautifulSoup

class Link2Doc(object):
    def __init__(self):
        self.pp = PreProcessor()

    def get_doc(self, link):
        try:
            start = time.time()
            print('***************')
            print(link)
            print('***************')
            r = requests.get(link)
            print('***************')
            print('STATUS CODE')
            print(r.status_code)
            print('***************')
            if not r.status_code == requests.codes.ok:
                return []
            soup = BeautifulSoup(r.text, 'html.parser')
            self.strip_crap(soup)
            doc = self.pp.pre_process(soup.get_text())
            print('***************')
            print(doc)
            print('***************')
            end = time.time()
            print('DONE WITH REQUEST + PROCESSING (ms):')
            print(end - start)
            return doc
        except:
            print('***************')
            print('***************')
            print('***************')
            print('Exception raised')
            print('***************')
            print('***************')
            print('***************')
            return []

    def strip_crap(self, soup):
        [ e.decompose() for e in soup.findAll(['head', 'script', 'link', 'meta']) ]
>>>>>>> Add initial version for category extraction
