import os
import config
import requests


CATEGORY_LINKS_DIRECTORY = config.get('resources', 'category_links')
GOOGLE_API_KEY = 'AIzaSyB5rnBkhckTkW7vByO8oA42AJd0pAqZuNA'
GOOGLE_CSE_ID = '009041204416826712200:az6a1takyjk'
GOOGLE_CSE_LINK_LIMIT = 10
GOOGLE_CSE_URL = 'https://www.googleapis.com/customsearch/v1'

COUNTRY_CODE_NETHERLANDS = 'countryNL'

MAX_NUMBER_OF_LINKS = 100
OFFSET = 10


class CategoryLinksCollector(object):
    def __init__(self, queries, filename):
        if isinstance(queries, list) and isinstance(queries[0], tuple):
            self.queries = queries
        else:
            raise Exception('The queries parameter should be a list of tuples')

        self.file = open(os.path.join(CATEGORY_LINKS_DIRECTORY, filename + '.txt'), 'a')
        self.url_parameters = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'fileType': 'html',
            'num': GOOGLE_CSE_LINK_LIMIT,
            'cr': COUNTRY_CODE_NETHERLANDS
        }

    def add_query(self, query):
        self.queries.append(query)

    def collect_urls(self, query):
        self.set_query(query[0])
        limit = query[1] if query[1] <= MAX_NUMBER_OF_LINKS else MAX_NUMBER_OF_LINKS

        offset = 1
        while offset < limit:
            self.execute_search(offset)
            offset += OFFSET

    def set_query(self, query):
        self.url_parameters['q'] = 'allintext: ' + query

    def execute_search(self, offset):
        self.url_parameters['start'] = offset
        r = requests.get(GOOGLE_CSE_URL, params=self.url_parameters)
        json = r.json()

        try:
            self.parse_urls(json['items'])
        except Exception as e:
            print(str(e))
            print(r.json())

    def parse_urls(self, items):
        for item in items:
            self.write_to_file(item['link'])

    def run(self):
        for q in self.queries:
            self.collect_urls(q)

        self.file.close()

    def write_to_file(self, url):
        self.file.write(url + '\n')
