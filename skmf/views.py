from flask import render_template
from skmf import app

@app.route('/')
@app.route('/index')
def index():
    return 'Index Page'

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
