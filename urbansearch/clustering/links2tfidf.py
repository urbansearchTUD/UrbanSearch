import os

import config
from .link2doc import Link2Doc
from .relationextractor import RelationExtractor

MODELS_DIRECTORY = config.get('resources', 'models')


class Links2Tfidf(object):
    def __init__(self, filename):
        self.filename = os.path.join(MODELS_DIRECTORY, filename)
        self.rex = RelationExtractor()

    def create_model(self):
        l2d = Link2Doc()

        with open(self.filename) as f:
            for line in f:
                print('********************')
                print(line)
                print('********************')
                doc = l2d.get_doc(line)
                self.rex.extend_dictionary(doc)

            self.rex.init_tfidf_model()
            self.rex.tfidf_model.save(self.filename)
