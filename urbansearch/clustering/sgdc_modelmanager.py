from nltk.corpus.stopwords import words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import f_classif, SelectPercentile
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from modelmanager import ModelManager


class SGDCModelManager(ModelManager):
    """
    An implementation of the ModelManager base class which uses a SVM trained
    with SGD as its default classifier.
    """

    def __init__(self, filename=None):
        super().__init__(filename)

        if not filename:
            self.clf = Pipeline([
                ('tfidf', TfidfVectorizer(stop_words=words('dutch'))),
                ('anova', SelectPercentile(f_classif)),
                ('clf', SGDClassifier(alpha=0.0001,
                                      average=False,
                                      class_weight=None,
                                      epsilon=0.1,
                                      eta0=0.0,
                                      fit_intercept=True,
                                      l1_ratio=0.15,
                                      learning_rate='optimal',
                                      loss='log',
                                      n_iter=5,
                                      n_jobs=1,
                                      penalty='l2',
                                      power_t=0.5,
                                      random_state=None,
                                      shuffle=True,
                                      verbose=0,
                                      warm_start=False))
            ])
