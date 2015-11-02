"""Semantic Knowledge Management Framework by Brendan Sweeney, CSS 593, 2015.

This package is designed to interface with a Web server and a SPARQL endpoint
to allow users to visually craft SPARL queries in order to identify relation-
ships between sets of data. It also aims to guide the user in defining new
relationships between resources in order to produce more meaningful queries.

Modules:
def_conf.py -- List of configuration defaults for Flask framework.
views.py -- Web page views for the Flask framework to render.
test.test_flask.py -- Unit tests for the Flask interface.
test.test_sparql.py -- Unit tests for the SAPRQLWrapper interface.
"""

# Temporary imports for database initialization
import sqlite3
from contextlib import closing

from flask import Flask, g
from SPARQLWrapper import SPARQLWrapper #, JSON

app = Flask(__name__)
app.config.from_object('skmf.def_conf')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
# Flask requires this circular import in most situations
from skmf import views
# Suppress warnings about unused circular import
assert views == views


def connect_sparql():
    """Return a connection to a SPARQL endpoint."""
    return SPARQLWrapper('http://localhost:9000/sparql/')


def connect_db():
    """Return a connection to a testing SQLite3 database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Close the SQLite3 database connection."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """Create a database connection before a Flask request."""
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """Close the database connection after a Flask request is closed."""
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
