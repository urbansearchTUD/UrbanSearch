import pickle


class PickleUtils(object):
    """
    Pickle utils class. Provides usefull helpers for working with pickled
    documents. Serves as a base class for more specific pickle utils
    """

    def load(self, filename):
        """
        Unpickle an object from filename

        :param filename: The filename from which we want to unpickle the object
        """
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except:
            raise Exception('Loading object from {} failed'.format(filename))


    def save(self, obj, filename):
        """
        Pickle an object to filename

        :param obj: The object to be pickled
        :param filename: The filename to which we want to pickle the object
        """
        try:
            with open(filename, 'wb') as f:
                pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        except:
            raise Exception('Saving object to {} failed'.format(filename))
