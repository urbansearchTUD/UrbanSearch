from nltk.corpus import stopwords as sw
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import f_classif, SelectPercentile
from sklearn.linear_model import SGDClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline


class PipelineFactory(object):
    """docstring for PipelineFactory."""
    def get(self, pipe):
        if pipe == 'binary':
            return self.get_binary()
        elif pipe == 'sgdc':
            return self.get_sgdc()
        elif pipe == 'mnb':
            return self.get_mnb()
        else:
            return None

    def get_binary(self):
        return Pipeline([
            ('tfidf', TfidfVectorizer(stop_words=sw.words('dutch'), norm='l2', use_idf=True)),
            ('feat_select', SelectPercentile(percentile=10)),
            ('clf', OneVsRestClassifier(SGDClassifier(alpha=0.0001,
                                                      average=False,
                                                      class_weight=None,
                                                      epsilon=0.1,
                                                      eta0=0.0,
                                                      fit_intercept=True,
                                                      l1_ratio=0.15,
                                                      learning_rate='optimal',
                                                      loss='log',
                                                      n_iter=10,
                                                      n_jobs=1,
                                                      penalty='l2',
                                                      power_t=0.5,
                                                      random_state=None,
                                                      shuffle=True,
                                                      verbose=0,
                                                      warm_start=False
            )))
        ])


    def get_mnb(self):
        pass

    def get_sgdc(self):
        return Pipeline([
            ('tfidf', TfidfVectorizer(stop_words=sw.words('dutch'), norm='l2', use_idf=True)),
            ('feat_select', SelectPercentile(percentile=10)),
            ('clf', SGDClassifier(alpha=0.0001,
                                  average=False,
                                  class_weight=None,
                                  epsilon=0.1,
                                  eta0=0.0,
                                  fit_intercept=True,
                                  l1_ratio=0.15,
                                  learning_rate='optimal',
                                  loss='log',
                                  n_iter=10,
                                  n_jobs=1,
                                  penalty='l2',
                                  power_t=0.5,
                                  random_state=None,
                                  shuffle=True,
                                  verbose=0,
                                  warm_start=False))
        ])
