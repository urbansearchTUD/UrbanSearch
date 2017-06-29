import config

from urbansearch.clustering.modelmanager import ModelManager
from urbansearch.clustering.pipeline_factory import PipelineFactory

CATEGORIES = config.get('score', 'categories')


class BinaryModelManager(ModelManager):
    def __init__(self, filename=None):
        super().__init__(filename)
        pf = PipelineFactory()
        self.clf = pf.get('binary')

    # def optimise(self, parameters):
    #     pass

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

    def score(self):
        """
        Test the objects classifier
        """
        if self.clf and self.x_test and self.y_test:
            return self.clf.score(self.x_test, self.y_test)

    def test(self):
        """
        Test the objects classifier
        """
        if self.clf and self.x_test and self.y_test:
            return self.score(self.x_test, self.y_test)

    def train(self):
        """
        Train the objects classifier
        """
        if self.clf and self.x_train and self.y_train:
            self.clf.fit(self.x_train, self.y_train)

    def validate(self):
        """
        Validate the objects classifier
        """
        if self.clf and self.x_validate:
            return self.predict(self.x_validate)
