[![Build Status](https://travis-ci.org/urbansearchTUD/UrbanSearch.svg?branch=master)](https://travis-ci.org/urbansearchTUD/UrbanSearch) [![Coverage Status](https://coveralls.io/repos/github/urbansearchTUD/UrbanSearch/badge.svg?branch=travis)](https://coveralls.io/github/urbansearchTUD/UrbanSearch?branch=travis)

# UrbanSearch
This repository contains the code for the UrbanSearch project. The project involves extracting intercity relationships from open data and visualising them. Initially, [Common Crawl](https://commoncrawl.org) is used as document corpus. Clearly this is a large data set, therefore this repository does not contain the data.

## Setup
The project runs Python 3.5. It is most appropriate to use a virtual environment to keep your PC clean.

A useful tool for creating and managing virtual environments is [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).
To create a virtual environment: `mkvirtualenv <name>`. If your default Python version is not 3.5, make sure it is installed and do `mkvirtualenv -p <python3.5 binary path> <name>`.

Any dependencies will be listed in the file `requirements.txt` and can be installed through pip (included in the virtual environment): `pip install -r requirements.txt`
