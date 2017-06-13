import logging.config
import os

import yaml

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.config', 'urbansearch')
CONFIG_FILE = 'urbansearch.yml'

TEST = False
TEST_CONFIG_PATH = BASE_DIR
TEST_CONFIG_FILE = 'test_config.yml'

DEFAULTS_FILE = 'defaults.yml'
SYS_CONFIG_PATH = os.path.join(os.sep, 'etc', 'urbansearch')
CONFIG = {}

LOGGER = None


def _merge(a, b):
    # Merges two dictionaries and allows for nested dictionaries
    for k, v in a.items():
        if k in b:
            if isinstance(v, dict):
                a[k] = _merge(v, b[k])
            else:
                a[k] = b[k]
    return a


def _load_test_config():
    # Only if TEST is set, use the test config (from load_custom_config)
    with open(os.path.join(TEST_CONFIG_PATH, TEST_CONFIG_FILE)) as f:
        return yaml.load(f)


def _load_default_config():
    # Might (but should never) throw an error if the defaults file is
    # badly configured
    with open(os.path.join(BASE_DIR, DEFAULTS_FILE)) as f:
        return yaml.load(f)


def _load_custom_config():
    if TEST:
        return _load_test_config()

    # Try to load existing config or create a new empty settings file
    system_config = _load_system_config()

    if system_config:
        return system_config
    else:
        return _load_user_config()


def _load_user_config():
    try:
        with open(os.path.join(CONFIG_PATH, CONFIG_FILE), 'r+') as f:
            # Concatenate config, override defaults with YAML values
            return yaml.load(f)
    except FileNotFoundError:
        # Create settings directory if it does not exist
        pass


def _load_system_config():
    try:
        with open(os.path.join(SYS_CONFIG_PATH, CONFIG_FILE), 'r+') as f:
            # Concatenate config, override defaults with YAML values
            return yaml.load(f)
    except Exception as e:
        pass

def _load_config():
    # Fills the global CONFIG dictionary using default and custom config
    # Returns an error if the custom config is invalid
    global CONFIG
    try:
        cfg = _load_default_config()
        custom_cfg = _load_custom_config()
        if custom_cfg:
            CONFIG = _merge(cfg, custom_cfg)
        else:
            CONFIG = cfg
    except yaml.YAMLError as exc:
        # Try to point to the line that threw an error
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            return 'Error in YAML at position: ({}:{})'.format(mark.line + 1,
                                                               mark.column + 1)


def _get_config():
    # Loads the config if necessary and returns it
    if not bool(CONFIG):
        global LOGGER
        err = _load_config()

        # Now configure logging
        logging.config.dictConfig(CONFIG['logging'])

        # And logging is ready to use
        LOGGER = logging.getLogger('config')

        # If an error occurred during YAML parsing, log it
        if err:
            LOGGER.error(err)
        else:
            LOGGER.info('Configuration has been successfully loaded')
    return CONFIG


def get(entity, param):
    """
    Returns the configuration value belonging to a specified entity
    (e.g. neo4j) and parameter (e.g. host).

    :param entity: The configuration entity
    :param param: The configuration parameter
    :return: The configuration value
    :raises ValueError if a requested parameter is not configured
    """
    try:
        value = _get_config()[entity][param]
        LOGGER.debug('Found config: {}:{} => {}'.format(entity, param, value))
        return _get_config()[entity][param]
    except KeyError:
        # Should _never_ happen in production!
        msg = 'Parameter {} is not present for entity {}!'.format(param,
                                                                  entity)
        LOGGER.critical(msg)
        raise ValueError(msg)
