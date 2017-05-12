import logging.config
import os

import yaml

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.config', 'urbansearch')
CONFIG_FILE = 'urbansearch.yml'

# The configuration parameters. They can all be overridden in the YAML config file.
# For Neo4j, it is required to override the settings since they have been left empty
# for security purposes.
CONFIG = {
    'neo4j': {
        'host': '',
        'bolt_uri': '',
        'username': '',
        'password': '',
    },
    'resources': {
        'test': os.path.join(BASE_DIR, 'tests', 'resources'),
    },
    'logging': {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(levelname)s %(module)s] %(asctime)s || %(message)s',
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'urbansearch.log'),
                'maxBytes': 10000000,
                'backupCount': 5,
                'formatter': 'default',
            },
            'console': {
                'level': 'WARN',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
        },
        'loggers': {
            'urbansearch': {
                'handlers': ['file', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'config': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'clustering': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
            'filtering': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
            'gathering': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    },
}

# Keep track of whether the system has been configured
_state = False

# Try to load existing config or create a new settings file including all parameters, but with empty values
try:
    with open(os.path.join(CONFIG_PATH, CONFIG_FILE), 'r+') as f:
        # Concatenate config, override defaults with YAML values
        CONFIG = {**CONFIG, **yaml.load(f)}
        _state = True
except FileNotFoundError:
    # Create settings directory if it does not exist
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)
    with open(os.path.join(CONFIG_PATH, CONFIG_FILE), 'w') as f:
        yaml.dump(CONFIG, f, default_flow_style=False)

# Now configure logging
logging.config.dictConfig(CONFIG['logging'])

# And logging is ready to use
logger = logging.getLogger(__name__)


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
        logger.error(msg)
        raise SystemError(msg)

    try:
        value = CONFIG[entity][param]
        logger.debug('Found config: %s:%s => %s' % (entity, param, str(value)))
        return CONFIG[entity][param]
    except KeyError:
        # Should _never_ happen in production!
        msg = 'Parameter %s is not present for entity %s!' % (param, entity)
        logger.critical(msg)
        raise ValueError(msg)
