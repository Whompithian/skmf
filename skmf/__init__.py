"""Semantic Knowledge Management Framework by Brendan Sweeney, CSS 593, 2015.

This package is designed to interface with a Web server and a SPARQL endpoint
to allow users to visually craft SPARQL queries in order to identify relation-
ships between sets of data. It also aims to guide the user in defining new
relationships between resources in order to produce more meaningful queries.
Flask, which is used as the underlying Web framework, is capable of launching
its own server, but it is advised to interface with a proper Web server for any
production use. There is no builtin SPARQL endpoint functionality, so the end-
point defined in the configuration must be accessible to and writable by this
package.

Modules:
    conf_def: List of configuration defaults for Flask framework.
    conf_test: List of test configuration defaults for Flask framework.
    forms: WTForms definitions for use in Flask views.
    i18n.en_US: Symbols to represent strings written in US English prose.
    sparqler: Handle forming and executing SPARQL queries.
    test.test_skmf: Unit tests for the Flask and SPARQL interfaces.
    views: Web page views for the Flask framework to render.

Functions:
    before_request: Perform standard setup before executing a Flask request.
    connect_sparql: Establish connection to SPARQL endpoint.
    teardown_request: Perform standard cleanup after Flask request closes.
"""

from flask import Flask, g

app = Flask(__name__)
"""Web framework application for handling views and sessions."""
app.config.from_object('skmf.conf_def')
app.config.from_envvar('FLASK_SETTINGS', silent=True)

from skmf import views
from skmf.sparqler import SPARQLER

# Suppress warnings about unused circular import
assert views


def connect_sparql():
    """Return a connection to a SPARQL endpoint.
    
    A connection is attempted to a SPARQL endpoint based on parameters defined
    in the configuration source. If a parameter was not defined, an exception
    is caught and re-raised with a description of the problem. Execution cannot
    continue without connection to the endpoint. It is assumed that the SPARQL
    endpoint is available and allows updates. It is also assumed that query and
    update requests are sent to the same port on a single host and that only
    the path may differ.
    
    Returns:
        SPARQLER: a connection to a query and update SPARQL endpoint.
    
    Raises:
        KeyError: if a connection component was not defined in the config.
    """
    try:
        return SPARQLER(endpoint = app.config['SPARQL_ENDPOINT']
                                 + app.config['SPARQL_QUERY'],
                        updateEndpoint = app.config['SPARQL_ENDPOINT']
                                       + app.config['SPARQL_UPDATE'])
    except KeyError as e:
        raise KeyError(str(e) + ' not defined in Flask config')


@app.before_request
def before_request():
    """Establish a SPARQL endpoint connection before any Flask requests.
    
    A connection to a SPARQL endpoint is established and placed in the global
    context, g. This makes the triplestore available for any request that may
    require it. Since SPARQL requests are made with HTTP GET and POST commands,
    there is no subsequent teardown needed for a SPARQL connection.
    """
    g.sparql = connect_sparql()


@app.teardown_request
def teardown_request(exception):
    """Not used, since SPARQL endpoint connections do not require teardown."""
    pass
