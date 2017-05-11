import os

import yaml

CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.config', 'urbansearch')
CONFIG_FILE = 'urbansearch.yml'

# Create settings directory if it does not exist
if not os.path.exists(CONFIG_PATH):
    os.makedirs(CONFIG_PATH)

# Keep track of whether the system has been configured
_state = False

# The configuration parameters
CONFIG = {
    'neo4j': {
        'host': '',
        'bolt_uri': '',
        'username': '',
        'password': '',
    },
    'resources': {
        'test': '',
    },
}

# Try to load existing config or create a new settings file including all parameters, but with empty values
try:
    with open('%s%s' % (CONFIG_PATH, CONFIG_FILE), 'r+') as f:
        CONFIG = yaml.load(f)
        _state = True
except FileNotFoundError:
    # TODO: log instead of print as soon as logger is implemented
    print('Creating config file in %s...' % CONFIG_PATH)
    print('Make sure to fill it!')
    with open('%s%s' % (CONFIG_PATH, CONFIG_FILE), 'w') as f:
        yaml.dump(CONFIG, f, default_flow_style=False)


def get(entity, param):
    """
    Returns the configuration value belonging to a specified entity (e.g. neo4j) and parameter (e.g. host).

    Raises a SystemError if the system has not been configured.
    Raises a ValueError if a requested parameter is not configured.

    :param entity: The configuration entity
    :param param: The configuration parameter
    :return: The configuration value
    """
    if not _state:
        raise SystemError('No configuration present in %s%s' % (CONFIG_PATH, CONFIG_FILE))

    try:
        return CONFIG[entity][param]
    except KeyError:
        # Should _never_ happen in production!
        raise ValueError('Parameter %s is not present for entity %s!' % (param, entity))
