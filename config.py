import os

import yaml

from urbansearch.logging import logutils

LOGGER = logutils.getLogger(__name__)
logutils.add_handlers(LOGGER)
logutils.set_loglevel(LOGGER, logutils.logging.DEBUG)

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
    with open(os.path.join(CONFIG_PATH, CONFIG_FILE), 'r+') as f:
        CONFIG = yaml.load(f)
        LOGGER.info('Loading configuration file')
        _state = True
except FileNotFoundError:
    LOGGER.info('Creating config file in %s...\nMake sure to fill it!' % CONFIG_PATH)
    with open(os.path.join(CONFIG_PATH, CONFIG_FILE), 'w') as f:
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
        msg = 'No configuration present in %s' % os.path.join(CONFIG_PATH, CONFIG_FILE)
        LOGGER.error(msg)
        raise SystemError(msg)

    try:
        value = CONFIG[entity][param]
        LOGGER.debug('Found config: %s:%s => %s' % (entity, param, str(value)))
        return CONFIG[entity][param]
    except KeyError:
        # Should _never_ happen in production!
        msg = 'Parameter %s is not present for entity %s!' % (param, entity)
        LOGGER.critical(msg)
        raise ValueError(msg)
