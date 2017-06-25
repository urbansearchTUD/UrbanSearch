import config
from datetime import datetime
import os
import math
import pickle

from urbansearch.utils.p_utils import PickleUtils

CATEGORIES = config.get('score', 'categories')
DATA_SETS_DIRECTORY = config.get('resources', 'data_sets')
MODELS_DIRECTORY = config.get('resources', 'models')


class DatasetPickleUtils(PickleUtils):
    """
    DatasetPickleUtils
    """

    def append_to_inputs(self, text, filename=None, category=None):
        """
        Append a text to the list in the specified file

        :param filename: appends the text to the list in the specified file
        :param text: the text to append
        """
        if not filename and not category:
            raise Exception('Filename or category should be specified')

        filename = self.category_to_file(category) if category else filename
        dataset = self.load(filename)

        if isinstance(dataset['inputs'], list):
            dataset['inputs'] += [text]
            self.save(dataset, filename)
        else:
            raise Exception('Inputs not a list')

    def append_list_to_inputs(self, texts, filename=None, category=None):
        """
        Append a list off texts to the list in the specified file

        :param filename: appends the texts to the list in the specified file
        :param text: the texts to append
        """
        if isinstance(texts, list) and (filename or category):
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
        Return the filename for the category

        :param category: the category for which we want the filename
        :return: filename for the category
        """
        return '{}.pickle'.format(category)

    def filename_to_path(self, filename):
        """
        Return the path for the file

        :param category: the file for which we want the path
        :return: path for the supplied filename
        """
        return os.path.join(DATA_SETS_DIRECTORY, filename)

    def init_categoryset(self, category, inputs=None):
        """
        Initialize a new dataset

        :param filename: the filename of the file in which we want to store
        the new object
        """
        inputs = inputs if inputs and isinstance(inputs, list) else []

        categoryset = {
            'output': category,
            'inputs': inputs
        }

        self.save(categoryset, self.category_to_file(category))

    def init_categorysets(self):
        """
        Initialize a categoryset for all the default categories.
        The files will contain no input documents.
        """
        for category in CATEGORIES:
            self.init_categoryset(category)

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

        :return filename: Path of the saved dataset
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

        filename = 'data.{}.pickle'.format(datetime.now().strftime('%d%m%Y'))
        self.init_dataset(filename, inputs=x, outputs=y)

        return filename

    @staticmethod
    def _load_files_with_min(categories):
        # Loads pickle files for every catory and reports the smallest
        # category data set
        sets = {}
        min_size = math.inf
        for category in categories:
            try:
                data = self.load(self.category_to_file(category))
                sets[category] = data['inputs']
                if len(sets[category]) < min_size:
                    min_size = len(sets[category])
            except:
                pass
        return sets, min_size

    @staticmethod
    def _generate_file_name(default):
        # Generates a file name for the pickle file
        if not default:
            filename = 'data.{}.pickle'.format(datetime.now().strftime('%d%m%Y'))
        else:
            filename = 'data.default.pickle'


    def generate_equal_dataset(self, default=False):
        """
        Generates a dataset which combines the files from the predefined
        categories and pickles a object containing 'inputs' and 'outputs'
        attributes. The dataset will contain equally sized sets for every
        category, with every set being scaled to the size of the smallest
        dataset.

        :return filename: Path of the saved dataset
        """
        categories = list(CATEGORIES)
        categories.pop(categories.index('other'))
        x = []
        y = []

        sets, min_size = self._load_files_with_min(categories)

        for cat, s in sets.items():
            x += s[:min_size]
            y += ([cat] * min_size)

        self.init_dataset(filename, inputs=x, outputs=y)

        return self._generate_file_name(default)

    def load(self, filename):
        """
        Dataset load function, overwrites the p_utils load function

        :param filename: the file which we want to load
        :return: The object saved in the file
        """
        return super().load(self.filename_to_path(filename))

    def persist_categorysets(self):
        """
        Saves the current categorysets to files that will not be erased when
        init_categorysets is called. The files are saved in the following
        format: $CATEGORY.$DATE_OF_SAVE.pickle
        """
        for category in CATEGORIES:
            filename = self.category_to_file(category)
            data = self.load(filename)
            self.save(data, '{}.{}.pickle'.format(category,
                                            datetime.now().strftime('%d%m%Y')))

    def save(self, obj, filename):
        """
        Dataset save function, overwrites the p_utils save function

        :param obj: the object we want to save/pickle
        :param filename: the filename to which we want to save the object
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
