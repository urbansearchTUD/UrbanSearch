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


def test_category_with_threshold():
    ct = classifytext.ClassifyText()
    p = {'a': 0.2, 'b': 0.49}
    res = ct.category_with_threshold(p, 0.49)
    assert 'b' == res
    assert isinstance(res, str)
    res = ct.category_with_threshold(p, 0.5)
    assert 'Other' == res
    assert isinstance(res, str)


def test_categories_above_threshold():
    ct = classifytext.ClassifyText()
    p = {'a': 0.2, 'b': 0.49, 'c': 0.60}
    res = ct.categories_above_threshold(p, 0.3)
    assert set(res) == set(['b', 'c'])
    res = ct.categories_above_threshold(p, 0.61)
    assert ['Other'] == res
