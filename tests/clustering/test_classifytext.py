from numpy import ndarray
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from urbansearch.clustering import classifytext, modelmanager, mnb_modelmanager, sgdc_modelmanager


def test_init():
    ct = classifytext.ClassifyText()
    assert isinstance(ct.mm, sgdc_modelmanager.SGDCModelManager)
    assert isinstance(ct.mm.clf, Pipeline)
    assert isinstance(ct.mm.clf.named_steps['clf'], SGDClassifier)

def test_init_sgdc():
    ct = classifytext.ClassifyText(type=classifytext.SGDC)
    assert isinstance(ct.mm, sgdc_modelmanager.SGDCModelManager)
    assert isinstance(ct.mm.clf, Pipeline)
    assert isinstance(ct.mm.clf.named_steps['clf'], SGDClassifier)

def test_init_mnb():
    ct = classifytext.ClassifyText(type=classifytext.MNB)
    assert isinstance(ct.mm, mnb_modelmanager.MNBModelManager)
    assert isinstance(ct.mm.clf, Pipeline)
    # assert isinstance(ct.mm.clf.named_steps['clf'], MultinomialNB)

def test_predict():
    ct = classifytext.ClassifyText()
    p = ct.predict('This is a random text, shoppen, winkelen')
    assert isinstance(p, ndarray)
    assert isinstance(p[0], str)


def test_probability_per_category():
    ct = classifytext.ClassifyText()
    p = ct.probability_per_category('This is a random text, shoppen, winkelen')
    assert isinstance(p, dict)
    for category, prob in p.items():
        assert isinstance(category, str)
        assert isinstance(prob, float)
