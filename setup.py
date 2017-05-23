import sys

import nltk
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.test import test


def load_nltk_data():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('snowball_data')


class UrbanSearchInstall(install):
    def run(self):
        load_nltk_data()
        install.run(self)


class UrbanSearchTest(test):
    def initialize_options(self):
        test.initialize_options(self)
        load_nltk_data()

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(['-v', 'tests/'])
        sys.exit(errno)

setup(
    name='UrbanSearch',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/urbansearchTUD/UrbanSearch',
    license='GPL-3.0',
    author='urbanSearchTUD',
    author_email='',
    description='',
    tests_require=['pytest'],
    test_suite='tests/',
    cmdclass={
        'install': UrbanSearchInstall,
        'test': UrbanSearchTest
    },
)
