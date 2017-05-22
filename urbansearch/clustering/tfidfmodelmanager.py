import config
import os
from gensim import corpora, models

from decorators import list_required
from modelmanager import ModelManager

MODELS_DIRECTORY = config.get('resources', 'models')
TFIDF_MODEL_EXTENSION = '.tfidf_model'


class TFIDFModelManager(ModelManager):
    def __init__(self, name, texts=None, load=False):
        """
        TODO: documentation
        """
        super().__init__(name, texts, load=load)
        self.model = None
        if load:
            self.load()

    @list_required
    def extract(self, doc):
        """
        Extracts the TF-IDF score of the supplied document

        :param: doc
        :return: score
        """
        print('model eerts')
        print(self.model)
        if not self.model:
            self.init_model()

        print(self.model)
        print(doc)
        # print(type(self.model[self.doc_to_bow(doc)]))
        return self.model[self.doc_to_bow(doc)]

    def init_model(self):
        """
        Initialize the model
        """
        if self.corpus and self.dictionary and not self.model:
            self.model = models.TfidfModel(self.corpus, id2word=self.dictionary)

        return self.model

    def load(self):
        """
        Load saved model
        """
        super().load()
        try:
            self.model = models.TfidfModel(self.corpus, id2word=self.dictionary)
            #self.model.load(os.path.join(MODELS_DIRECTORY, self.name + '.tfidf_model'))
            print('joepiew')
        except:
            print('yoloooooo')
            self.model = models.TfidfModel(self.corpus, id2word=self.dictionary)
            # raise Exception('Model file not found for category: ' + self.name)

    def save(self):
        """
        Save the model
        """
        super().save()
        self.model.save(os.path.join(MODELS_DIRECTORY, self.name + TFIDF_MODEL_EXTENSION))
