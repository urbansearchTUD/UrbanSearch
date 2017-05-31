from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from urbansearch.clustering import modelmanager
from urbansearch.clustering import mnb_modelmanager


def test_init_no_file():
    mm = mnb_modelmanager.MNBModelManager()
    assert isinstance(mm, mnb_modelmanager.MNBModelManager)
    assert isinstance(mm.clf, Pipeline)
    assert isinstance(mm.clf.named_steps['clf'], MultinomialNB)

def test_init():
    mm = mnb_modelmanager.MNBModelManager('sgdcmodel.pickle')
    assert isinstance(mm, modelmanager.ModelManager)
    assert isinstance(mm.clf, Pipeline)
    assert isinstance(mm.clf.named_steps['clf'], SGDClassifier)
