import config
import os
import pickle
MODELS_DIRECTORY = config.get('resources', 'models')
TEST_SETS_DIRECTORY = config.get('resources', 'test_sets')
TRAINING_SETS_DIRECTORY = config.get('resources', 'training_sets')
VALIDATION_SETS_DIRECTORY = config.get('resources', 'validation_sets')


class ModelManager(object):
    """
    ModelManager base class.
    Should only be used to load saved models from disk.
    If a filename is passed this file will be used to load a pickeled
    classifier from that location on disk.
    """

    def __init__(self, filename=None):
        super(ModelManager, self).__init__()
        self.x_train = []
        self.y_train = []
        self.x_validate = []
        self.y_validate = []
        self.x_test = []
        self.y_test = []

        self.clf = self.load(filename) if filename else None

    def load(self, filename):
        """
        Load the classifier from the supplied file

        :param filename: the file containing the pickeled classifier instance
        :return: a scikit classifier object
        """
        with open(os.path.join(MODELS_DIRECTORY, filename), 'rb') as f:
            return pickle.load(f)

    def load_trainingset(self, filename):
        """
        Load a trainingset from the file and set the objects trainingset arrays

        :param filename: filename containing the trainingset
        """
        with open(os.path.join(TRAINING_SETS_DIRECTORY, filename), 'rb') as f:
            data = pickle.load(f)
            self.x_train = data['inputs']
            self.y_train = data['outputs']

    def load_testset(self, filename):
        """
        Load a trainingset from the file and set the objects trainingset arrays

        :param filename: filename containing the trainingset
        """
        with open(os.path.join(TEST_SETS_DIRECTORY, filename), 'rb') as f:
            data = pickle.load(f)
            self.x_test = data['inputs']
            self.y_test = data['outputs']

    def load_validationset(self, filename):
        """
        Load a trainingset from the file and set the objects trainingset arrays

        :param filename: filename containing the trainingset
        """
        with open(os.path.join(VALIDATION_SETS_DIRECTORY, filename),
                  'rb') as f:
            data = pickle.load(f)
            self.x_validate = data['documents']
            self.y_validate = data['categories']

    def predict(self, files):
        """
        Predict the category of the passed file

        :param files: the files for which we want to predict the category.
        :return: A list of categories for the passed in files.
        """
        if self.clf:
            return self.clf.predict(files)

    def probabilities(self, files):
        """
        Get the probabilities of the passed file belonging to the available
        categories.

        :param files: the files for which we want to predict the category.
        :return: A list of probabilities for the passed in files per category.
        """
        if self.clf:
            return self.clf.predict_proba(files)

    def save(self, filename):
        """
        Pickle the clf dictionary using the highest protocol available.

        :param filename: The filename where the pickeled classifier should be
        stored.
        """
        if self.clf:
            with open(os.path.join(MODELS_DIRECTORY, filename), 'wb') as f:
                pickle.dump(self.clf, f, pickle.HIGHEST_PROTOCOL)

    def test(self):
        """
        Test the objects classifier
        """
        if self.clf and self.x_test:
            self.predict(self.x_test)

    def train(self):
        """
        Train the objects classifier
        """
        if self.clf and self.x_train and self.y_train:
            self.clf.fit_transform(self.x_train, self.y_train)

    def validate(self):
        """
        Validate the objects classifier
        """
        if self.clf and self.x_validate:
            self.predict(self.x_validate)
