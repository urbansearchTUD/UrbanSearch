import config
import os
from gensim import corpora, models

from decorators import list_required
from modelmanager import ModelManager

MODELS_DIRECTORY = config.get('resources', 'models')
TFIDF_MODEL_EXTENSION = '.tfidf_model'


class LDAModelManager(ModelManager):
    """
    ModelManager extension for the LDA model
    """

    def __init__(self, name, texts=None):
        """
        TODO: documentation
        """
        super().__init__(name, texts)
        self.model = None

    @list_required
    def extract_tfidf(self, doc):
        """
        Extracts the TF-IDF score of the supplied document

        :param: doc
        :return: score
        """
        if not self.model:
            self.init_model()

        return self.model[self.doc_to_bow(doc)]

    def init_model(self):
        """
        TODO: documentation
        """
        if self.corpus and not self.model:
            self.model = models.TfidfModel(self.corpus)

        return self.model

    def save(self):
        """
        TODO: documentation
        """
        super().save()
        self.model.save(os.path.join(MODELS_DIRECTORY, self.name + TFIDF_MODEL_EXTENSION))
