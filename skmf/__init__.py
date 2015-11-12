"""Semantic Knowledge Management Framework by Brendan Sweeney, CSS 593, 2015.

This package is designed to interface with a Web server and a SPARQL endpoint
to allow users to visually craft SPARL queries in order to identify relation-
ships between sets of data. It also aims to guide the user in defining new
relationships between resources in order to produce more meaningful queries.
Flask, which is used as the underlying Web framework, is capable of launching
its own server, but it is advised to interface with a proper Web server for any
production use. There is no builtin SPARQL endpoint functionality, so the end-
point defined in the configuration must be accessible to and writable by this
package.

Modules:
    conf_def -- List of configuration defaults for Flask framework.
    conf_test -- List of test configuration defaults for Flask framework.
    forms -- WTForms definitions for use in Flask views.
    sparqler -- Handle forming and executing SPARQL queries.
    views -- Web page views for the Flask framework to render.
    i18n.en_US -- Symbols to represent strings written in US English prose.
    test.test_flask -- Unit tests for the Flask interface.
    test.test_sparql -- Unit tests for the SAPRQLWrapper interface.

Functions:
    connect_sparql -- Establish connection to SPARQL endpoint.
    before_request -- Perform standard setup before executing a Flask request
    teardown_request -- Perform standard cleanup after Flask request closes
"""

# Temporary imports for test database initialization
#import sqlite3
#from contextlib import closing

from flask import Flask, g

# Initialize the Web framework, load default config file, and overwrite default
# file with one provided in an environment variable, if available
app = Flask(__name__)
app.config.from_object('skmf.conf_def')
app.config.from_envvar('FLASK_SETTINGS', silent=True)
# Flask requires this circular import in most situations
from skmf import views
from skmf.sparqler import SPARQLER
# Suppress warnings about unused circular import
assert views == views


def connect_sparql():
    """Return a connection to a SPARQL endpoint.
    
    A connection is attempted to a SPARQL endpoint based on parameters defined
    in the configuration source. If a parameter was not defined, an exception
    is caught and re-raised with a description of the problem. Execution cannot
    continue without connection to the endpoint. It is assumed that the SPARQL
    endpoint is available and allows updates. It is also assumed that query and
    update requests are sent to the same port on a single host and that only
    the path may need to be different.
    
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


#def connect_db():
#    """Return a connection to a testing SQLite3 database."""
#    return sqlite3.connect(app.config['DATABASE'])


#def init_db():
#    """Create the tables for the testing SQLite3 database."""
#    with closing(connect_db()) as db:
#        with app.open_resource('schema.sql', mode='r') as f:
#            db.cursor().executescript(f.read())
#        db.commit()


@app.before_request
def before_request():
    """Establish a SPARQL endpoint connection before any Flask requests.
    
    A connection to a SPARQL endpoint is established and placed in the global
    context, g. This makes the triplestore available for any request that may
    require it. Since SPARQL requests are made with HTTP GET and POST commands,
    there is no subsequent teardown needed for a SPARQL connection.
    """
#    g.db = connect_db()
    g.sparql = connect_sparql()


@app.teardown_request
def teardown_request(exception):
    """Close the database connection after a Flask request has closed."""
    pass
#    db = getattr(g, 'db', None)
#    if db is not None:
#        db.close()
