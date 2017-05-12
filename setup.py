import sys
from setuptools import setup, find_packages

from setuptools.command.test import test


class PyTest(test):
    def initialize_options(self):
        test.initialize_options(self)

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main([])
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
    install_requires=[
        'pytest',
    ],
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest,
    }
)
