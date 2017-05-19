import requests
from bs4 import BeautifulSoup

class Link2Doc(object):

    def get_doc(self, link):
        print('***************')
        print(link)
        print('***************')
        r = requests.get(link)
        soup = BeautifulSoup(r.text, 'html.parser')
        self.strip_crap(soup)
        print('***************')

        print([word for word in soup.get_text().split() if len(word) < 37])
        print('***************')

    def strip_crap(self, soup):
        [ e.decompose() for e in soup.findAll(['head', 'script', 'link', 'meta']) ]
