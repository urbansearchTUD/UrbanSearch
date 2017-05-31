import config
import os

from urbansearch.clustering.mnb_modelmanager import MNBModelManager
from urbansearch.clustering.sgdc_modelmanager import SGDCModelManager
from urbansearch.clustering.text_preprocessor import PreProcessor

MAIN_CLASSIFIER_FILE = os.path.join(config.get('resources', 'models'),
                                    'sgdcmodel.pickle')
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
            self.mm = SGDCModelManager(filename=MAIN_CLASSIFIER_FILE)
        elif type == MNB:
            self.mm = MNBModelManager(filename=MAIN_CLASSIFIER_FILE)

    def predict(self, text, pre_processor=False):
        """
        Predict the class of the supplied text

        :param :text the text that needs to be classified
        :return: a prediction of the category for the passed text
        """
        if pre_processor:
            text = pre_processor(text)

        return self.mm.predict([text])

    def probability_per_category(self, text, pre_processor=False):
        """
        Predict the class of the supplied text

        :param :text the text that needs to be classified
        :return: a prediction of the category for the passed text
        """
        if pre_processor:
            text = pre_processor(text)

        return dict(zip(self.mm.clf.classes_,
                        self.mm.probabilities([text])[0]))
