import requests
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
