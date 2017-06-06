import config
import datetime
import os
import pickle

from .p_utils import PickleUtils

CATEGORIES = [
    'education',
    'leisure',
    'transportation',
    'collaboration',
    'commuting',
    'shopping',
    'residential_mobility',
    'other',
]
DATA_SETS_DIRECTORY = config.get('resources', 'data_sets')
MODELS_DIRECTORY = config.get('resources', 'models')


class DatasetPickleUtils(PickleUtils):
    """
    DatasetPickleUtils
    """

    def append_to_inputs(self, filename, text, category=None):
        """
        Append a text to the list in the specified file

        :param filename:
        :param text:
        """
        filename = self.category_to_file(category) if category else filename
        dataset = self.load(filename)

        if isinstance(dataset['inputs'], list):
            dataset['inputs'] += [text]
            self.save(dataset, filename)
        else:
            raise Exception('Inputs not a list')

    def append_list_to_inputs(self, filename, texts, category=None):
        """
        Append a list off texts to the list in the specified file

        :param filename:
        :param text:
        """
        if isinstance(texts, list):
            filename = self.category_to_file(category) if category else filename
            dataset = self.load(filename)

            if isinstance(dataset['inputs'], list):
                dataset['inputs'] += texts
                self.save(dataset, filename)
            else:
                raise Exception('Inputs not a list')
        else:
            raise Exception(
                'Texts should be a string got {}'.format(type(texts)))

    def category_to_file(self, category):
        """
        """
        return '{}.pickle'.format(category)

    def filename_to_path(self, filename):
        """
        """
        return os.path.join(DATA_SETS_DIRECTORY, filename)

    def init_categoryset(self, filename, output=None, inputs=None):
        """
        Initialize a new dataset

        :param filename: the filename of the file in which we want to store
        the new object
        """
        output = output if output and isinstance(output, str) else ''
        inputs = inputs if inputs and isinstance(inputs, list) else []

        categoryset = {
            'output': output,
            'inputs': inputs
        }

        self.save(categoryset, filename)

    def init_dataset(self, filename, inputs=None, outputs=None):
        """
        Initialize a new dataset

        :param filename: the filename of the file in which we want to store
        the new object
        """
        if not (inputs and outputs and len(inputs) == len(outputs)):
            inputs = []
            outputs = []

        dataset = {
            'outputs': outputs,
            'inputs': inputs
        }

        self.save(dataset, filename)

    def generate_dataset(self):
        """
        Generates a dataset which combines the files from the predefined
        categories and pickles a object containing 'inputs' and 'outputs'
        attributes
        """
        x = []
        y = []

        for category in CATEGORIES:
            try:
                data = self.load(self.category_to_file(category))
                x += data['inputs']
                y += ([category] * len(data['inputs']))
            except:
                pass

        i = datetime.datetime.now()
        self.init_dataset('data.{}.pickle'.format(i.strftime('%d%m%Y')),
                          inputs=x, outputs=y)

    def load(self, filename):
        """
        """
        return super().load(self.filename_to_path(filename))

    def save(self, obj, filename):
        """
        """
        super().save(obj, self.filename_to_path(filename))

    def set_output(self, filename, output):
        """
        Set the output attribute of the dataset

        :param filename: File containing the dataset
        :param output: New output parameter to be assigned
        """
        dataset = self.load(filename)
        dataset['output'] = output
        self.save(dataset, filename)
