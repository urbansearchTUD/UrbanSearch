from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from urbansearch.clustering import modelmanager
from urbansearch.clustering import sgdc_modelmanager


def test_init_no_file():
    mm = sgdc_modelmanager.SGDCModelManager()
    assert isinstance(mm, sgdc_modelmanager.SGDCModelManager)
    assert isinstance(mm.clf, Pipeline)
    assert isinstance(mm.clf.named_steps['clf'], SGDClassifier)

def test_init():
    mm = sgdc_modelmanager.SGDCModelManager('sgdcmodel.pickle')
    assert isinstance(mm, modelmanager.ModelManager)
    assert isinstance(mm.clf, Pipeline)
    assert isinstance(mm.clf.named_steps['clf'], SGDClassifier)
