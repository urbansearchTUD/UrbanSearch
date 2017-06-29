from nltk.corpus import stopwords as sw
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import f_classif, SelectPercentile
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from urbansearch.clustering.modelmanager import ModelManager
from urbansearch.clustering.pipeline_factory import PipelineFactory


class SGDCModelManager(ModelManager):
    """
    An implementation of the ModelManager base class which uses a SVM trained
    with SGD as its default classifier.
    """

    def __init__(self, filename=None):
        super().__init__(filename)
        self.pf = PipelineFactory()

        if not filename:
            self.clf = self.pf.get('sgdc')
