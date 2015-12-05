"""skmf.conf_def by Brendan Sweeney, CSS 593, 2015.

Set of default configuration values for the Flask component. These values are
placed in a separate file for maintainability and this default file may be
overridden by specifying a different file with the FLASK_SETTINGS environment
variable. This will prevent user settings from being overwritten by defaults in
the event of a package upgrade.
"""

DEBUG = True
"""bool: Set Flask to run in degug mode (True) or production mode (False)."""

TESTING = False
"""bool: Set Flask to run in test mode (True) or normal mode (False)."""

SECRET_KEY = 'replace this with a cryptographic random secret'
"""str: Seed for synchronizer token to mitigate cross-site request forgery."""

USERNAME = 'admin'
"""str: Default administrative user name."""

PASSWORD = 'default'
"""str: Default administrative password."""

SPARQL_HOST = 'localhost'
"""str: FQDN or IP address of the SPARQL endpoint."""

SPARQL_PORT = '9000'
"""str: Port on which the SPARQL endpoint is listening."""

SPARQL_QUERY = '/sparql/'
"""str: URL path for SPARQL queries on the endpoint."""

SPARQL_UPDATE = '/update/'
"""str: URL path for SPARQL updates on the endpoint."""

SPARQL_ENDPOINT = 'http://{}:{}'.format(SPARQL_HOST, SPARQL_PORT)
"""str: Full URL of the SPARQL endpoint."""

NAMESPACE = 'http://localhost/skmf'
"""str: Local namespace for subjects added to the datastore."""

PREFIXES = """
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX OntologyServices: <http://www.semanticweb.org/ontologies/2008/11/OntologyServices.owl#>
    PREFIX OntologySecurity2: <http://www.semanticweb.org/ontologies/2008/11/OntologySecurity.owl#3>
    PREFIX OntologySecurity3: <http://www.semanticweb.org/ontologies/2008/11/OntologySecurity.owl#2>
    PREFIX OntologySecurity4: <http://www.semanticweb.org/ontologies/2008/11/OntologySecurity.owl#2.5>
    PREFIX ontosec: <http://www.semanticweb.org/ontologies/2008/11/OntologySecurity.owl#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX owl2xml: <http://www.w3.org/2006/12/owl2-xml#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX VulnThreatAttack: <http://www.semanticweb.org/ontologies/2009/1/3/VulnThreatAttack.owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX skmf: <{namespace}#>
    """.format(namespace=NAMESPACE)
"""str: List of common prefixes to use with all SPARQL commands."""
