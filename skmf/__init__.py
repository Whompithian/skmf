import sqlite3
from flask import Flask, g
# Temporary import for database initialization
from contextlib import closing
from SPARQLWrapper import SPARQLWrapper #, JSON

app = Flask(__name__)
app.config.from_object('skmf.def_conf')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
from skmf import views
assert views == views


def connect_sparql():
    return SPARQLWrapper('http://localhost:9000/sparql/')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
