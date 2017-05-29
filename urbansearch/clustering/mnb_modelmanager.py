from nltk.corpus.stopwords import words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import f_classif, SelectPercentile
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from modelmanager import ModelManager


class MNBModelManager(ModelManager):
    """
    An implementation of the ModelManager base class which uses a Multinomial
    Naive Bayes classifier as its default classifier.
    """

    def __init__(self, filename=None):
        super().__init__(filename)

        if not filename:
            self.clf = Pipeline([
                ('tfidf', TfidfVectorizer(stop_words=words('dutch'))),
                ('anova', SelectPercentile(f_classif)),
                ('clf', MultinomialNB())
            ])
