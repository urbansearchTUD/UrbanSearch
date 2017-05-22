import requests
import time
from bs4 import BeautifulSoup

from text_preprocessor import PreProcessor

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
