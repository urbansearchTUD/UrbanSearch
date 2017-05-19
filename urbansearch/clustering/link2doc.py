import requests
from bs4 import BeautifulSoup

from text_preprocessor import PreProcessor

class Link2Doc(object):

    def get_doc(self, link):
        pp = PreProcessor()
        print('***************')
        print(link)
        print('***************')
        r = requests.get(link)
        soup = BeautifulSoup(r.text, 'html.parser')
        self.strip_crap(soup)
        doc = pp.pre_process(soup.get_text())
        print('***************')
        print(doc)
        print('***************')
        return doc

    def strip_crap(self, soup):
        [ e.decompose() for e in soup.findAll(['head', 'script', 'link', 'meta']) ]
