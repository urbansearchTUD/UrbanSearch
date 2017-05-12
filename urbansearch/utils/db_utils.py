from neo4j.v1 import GraphDatabase, basic_auth

import config

# Keep a global driver
_driver = None


def _get_session():
    global _driver
    # Reuse the driver when possible
    if _driver:
        return _driver.session()

    # If no driver is present, create a new one
    _driver = GraphDatabase.driver(config.get('neo4j', 'bolt_uri'),
                                   auth=basic_auth(config.get('neo4j', 'username'), config.get('neo4j', 'password')))
    return _driver.session()


def city_names():
    """
    :return: A list of city names, as retrieved from Neo4j
    """
    # Close sessions properly
    with _get_session() as session:
        return [c['name'] for c in session.run('MATCH (a:City) RETURN a.name AS name')]
