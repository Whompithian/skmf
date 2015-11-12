"""skmf.def_conf by Brendan Sweeney, CSS 593, 2015.

Set of default configuration values for the Flask component. These values are
placed in a separate file for maintainability and this default file may be
overridden by specifying a different file with the FLASKR_SETTINGS environment
variable. This will prevent user settings from being overwritten by defaults in
the event of a package upgrade.
"""

DATABASE = '/tmp/flaskr.db'
"""string: Full path to the database file to be created by init_db()."""

DEBUG = True
"""bool: Set Flask to run in degug mode (True) or production mode (False)."""

TESTING = True
"""bool: Set Flask to run in test mode (True) or normal mode (False)."""

SECRET_KEY = 'replace this with a cryptographic random secret'
"""string: Fake synchronizer token to mitigate cross-site request forgery."""

USERNAME = 'admin'
"""string: Username for running unit tests."""

PASSWORD = 'default'
"""string: Password for running unit tests."""

WTF_CSRF_ENABLED = False

SPARQL_HOST = 'localhost'
"""string: FQDN or IP address of the SPARQL endpoint."""

SPARQL_PORT = '9000'
"""string: Port on which the SPARQL endpoint is listening."""

SPARQL_QUERY = '/sparql/'
"""string: URL extension for SPARQL queries on the endpoint."""

SPARQL_UPDATE = '/update/'
"""string: URL extension for SPARQL updates on the endpoint."""

SPARQL_ENDPOINT = 'http://' + SPARQL_HOST + ':' + SPARQL_PORT
"""string: Full URL of the SPARQL endpoint."""

NAMESPACE = '<http://localhost/skmf#>'
"""string: Local namespace for subjects added to the datastore."""

PREFIXES = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skmf: {namespace}
    """.format(namespace=NAMESPACE)
"""string: List of common prefixes to use with all SPARQL commands."""
