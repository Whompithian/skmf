"""skmf.conf_test by Brendan Sweeney, CSS 593, 2015.

Set of testing configuration values for the Flask component. These values are
placed in a separate file for maintainability and this testing file may be used
to override the default by specifying it with the FLASKR_SETTINGS environment
variable. These values should only be used in a testing environment.
"""

DEBUG = True
"""bool: Set Flask to run in degug mode (True) or production mode (False)."""

TESTING = True
"""bool: Set Flask to run in test mode (True) or normal mode (False)."""

SECRET_KEY = 'replace this with a cryptographic random secret'
"""string: Fake synchronizer token to mitigate cross-site request forgery."""

USERNAME = 'admin'
"""string: Default administrative user name."""

PASSWORD = 'default'
"""string: Default administrative password."""

WTF_CSRF_ENABLED = False
"""bool: Disable CSRF protection to avoid having forms drop inputs."""

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

NAMESPACE = 'http://localhost/skmf'
"""string: Local namespace for subjects added to the datastore."""

PREFIXES = """
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skmf: <{namespace}#>
    """.format(namespace=NAMESPACE)
"""string: List of common prefixes to use with all SPARQL commands."""
