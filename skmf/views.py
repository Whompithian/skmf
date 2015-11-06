"""skmf.views by Armin Ronacher
(Modified by Brendan Sweeney, CSS 593, 2015.)

Currently, this is taken from the Flaskr tutorial and will need to be modified
as the frontend of the system is developed.
"""

from flask import render_template, request, redirect, url_for, \
                  abort, flash
#from flask_wtf import csrf
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.login import login_required, login_user, logout_user, current_user

from skmf import app, forms, g
from skmf.sparqler import sparql_query, sparql_insert
from skmf.user import User
import skmf.i18n.en_US as lang

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
    return render_template('show_tags.html',
                           title=lang.viewTagTitle, entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
#    if not session.get('logged_in'):
    if not current_user.is_authenticated:
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
    if form.validate_on_submit():
        user = User.get(form.username.data)
        if not user:
            # Make invalid user take same time as wrong password
            bcrypt.generate_password_hash(form.password.data)
            error = lang.viewLoginInvalid
        elif not bcrypt.check_password_hash(user.hashpass, form.password.data):
            error = lang.viewLoginInvalid
        else:
            user.authenticated = True
            login_user(user)
            flash('{0!s} {1!s}'.format(lang.viewLoginWelcome, user.name))
            return redirect(request.args.get('next') or url_for('show_tags'))
    return render_template('login.html', title='Login', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    flash(lang.viewLogoutLoggedout)
    return redirect(url_for('show_entries'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def show_users():
    """Manage user information in the datastore."""
    form = forms.CreateUserForm()
    if form.is_submitted() and form.validate():
        user = User(form.username.data,
                    bcrypt.generate_password_hash(form.password.data))
        flash(user.hashpass)
#    entries = sparql_query()
    return render_template('show_users.html', title='Manage Users', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


#@csrf.error_handler
#def csrf_error(reason):
#    return render_template('csrf_error.html', reason=reason), 400


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
