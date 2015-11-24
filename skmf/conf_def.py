"""skmf.conf_def by Brendan Sweeney, CSS 593, 2015.

Set of default configuration values for the Flask component. These values are
placed in a separate file for maintainability and this default file may be
overridden by specifying a different file with the FLASK_SETTINGS environment
variable. This will prevent user settings from being overwritten by defaults in
the event of a package upgrade.
"""

DATABASE = '/tmp/flaskr.db'
"""str: Full path to the database file to be created by init_db()."""

DEBUG = True
"""bool: Set Flask to run in degug mode (True) or production mode (False)."""

TESTING = False
"""bool: Set Flask to run in test mode (True) or normal mode (False)."""

SECRET_KEY = 'replace this with a cryptographic random secret'
"""str: Seed for synchronizer token to mitigate cross-site request forgery."""

USERNAME = 'admin'
"""str: Username for running unit tests."""

PASSWORD = 'default'
"""str: Password for running unit tests."""

SPARQL_HOST = 'localhost'
"""str: FQDN or IP address of the SPARQL endpoint."""

SPARQL_PORT = '9000'
"""str: Port on which the SPARQL endpoint is listening."""

SPARQL_QUERY = '/sparql/'
"""str: URL extension for SPARQL queries on the endpoint."""

SPARQL_UPDATE = '/update/'
"""str: URL extension for SPARQL updates on the endpoint."""

SPARQL_ENDPOINT = 'http://' + SPARQL_HOST + ':' + SPARQL_PORT
"""str: Full URL of the SPARQL endpoint."""

NAMESPACE = 'http://localhost/skmf'
"""str: Local namespace for subjects added to the datastore."""

PREFIXES = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skmf: <{namespace}#>
    """.format(namespace=NAMESPACE)
"""str: List of common prefixes to use with all SPARQL commands."""
