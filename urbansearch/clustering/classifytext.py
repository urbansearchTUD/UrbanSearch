import config
import os

from urbansearch.clustering.mnb_modelmanager import MNBModelManager
from urbansearch.clustering.sgdc_modelmanager import SGDCModelManager
from urbansearch.clustering.text_preprocessor import PreProcessor

DEFAULT_CLASSIFIER = config.get('classification', 'default_classifier')
MNB = 'mnb'
SGDC = 'sgdc'


class ClassifyText(object):

    """
    The ClassifyText class returns an object which lets users predict the
    category of files. The object loads a pre-trained model.
    """

    def __init__(self, type=None):
        """
        Initialize the ClassifyTextAPI with the MAIN_CLASSIFIER_FILE.
        This file contains the main trained classifier of this project.
        This class exposes a simple API that lets users easily predict
        the category a file belongs to.

        :param type: The type of classifier to load. If no type is supplied
        the default is "sgdc".
        """
        super(ClassifyText, self).__init__()

        if not type or type == SGDC:
            self.mm = SGDCModelManager(filename=DEFAULT_CLASSIFIER)
        elif type == MNB:
            self.mm = MNBModelManager(filename=DEFAULT_CLASSIFIER)

    def predict(self, text, pre_processor=None):
        """
        Predict the class of the supplied text

        :param :text the text that needs to be classified
        :return: a prediction of the category for the passed text
        """
        if pre_processor:
            text = pre_processor(text)

        return self.mm.predict([text])

    def probability_per_category(self, text, pre_processor=None):
        """
        Predict the class of the supplied text

        :param :text the text that needs to be classified
        :return: a prediction of the category for the passed text
        """
        if pre_processor:
            text = pre_processor(text)

        return dict(zip(self.mm.clf.classes_,
                        self.mm.probabilities([text])[0]))

    def category_with_threshold(self, prob, threshold):
        """ Return category with highest probability above the threshold.
        If no category is above threshold category returned is 'Other'.

        :prob: Dict with category as key and probability as value
        :threshold: A threshold for the probability between 0 and 1
        :return: Key with highest probability if above threshold, otherwise
        returns 'Other'
        """
        assert 0 <= threshold <= 1

        key = max(prob.keys(), key=(lambda k: prob[k]))
        if prob.get(key) >= threshold:
            return key
        else:
            return "Other"

    def categories_above_threshold(self, prob, threshold):
        """ Return categories with probabilities above the threshold.
        If no category is above threshold list only contains 'Other'.

        :prob: Dict with category as key and probability as value
        :threshold: A threshold for the probability between 0 and 1
        :return: List with categories above threshold, otherwise
        returns list with only 'Other' as element.
        """
        assert 0 <= threshold <= 1
        above = [k for (k, v) in prob.items() if v >= threshold]

        return above if above else ['Other']
