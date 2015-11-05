"""skmf.views by Armin Ronacher
(Modified by Brendan Sweeney, CSS 593, 2015.)

Currently, this is taken from the Flaskr tutorial and will need to be modified
as the frontend of the system is developed.
"""

from flask import render_template, request, session, redirect, url_for, \
                  abort, flash
#from flask_wtf import csrf
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.login import login_required, login_user, logout_user, current_user

from skmf import app, forms, g
from skmf.sparqler import sparql_query, sparql_insert
from skmf.user import User

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/')
@app.route('/index')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', title='Flaskr', entries=entries)


@app.route('/tags', methods=['GET', 'POST'])
def show_tags():
    """Use results from a form to add a tag entry to the datastore."""
    if request.method == 'POST':
        label = request.form['label']
        desc = request.form['description']
        flash(sparql_insert(label, desc))
    entries = sparql_query()
    return render_template('show_tags.html', title='Manage Tags', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = forms.LoginForm()
    if request.method == 'POST': #form.validate_on_submit():
        login_user(User('admin'), remember=True)
        flash('Logged in successfully.')
#        user = User.get(form.username.data)
#        if not user:
#            error = 'User not found: ' + form.username.data
#        elif not bcrypt.check_password_hash(user.hashpass, form.password.data):
#            error = 'Password incorrect: ' + form.password.data
#        else:
#            user.authenticated = True
#            login_user(user)
#            return redirect(url_for('show_tags'))
        return redirect(url_for('show_entries'))
    return render_template('login.html', title='Login', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    # The following line removes the session key, only if it exists
#    session.pop('logged_in', None)
    user = current_user
    user.authenticated = False
    logout_user()
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/users')
def show_users():
    """Manage user information in the datastore."""
#    if request.method == 'POST':
#        label = request.form['label']
#        desc = request.form['description']
#        flash(sparql_insert(label, desc))
#    entries = sparql_query()
    return render_template('show_users.html', title='Manage Users')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


#@csrf.error_handler
#def csrf_error(reason):
#    return render_template('csrf_error.html', reason=reason), 400


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
