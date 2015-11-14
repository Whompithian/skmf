"""skmf.views by Brendan Sweeney, CSS 593, 2015.

Define the views that are rendered by Flask to the end user. This controls what
action to take given a URL path provided by the user. Typically, a path will
result in the display of a Web page which is rendered from a template. Multiple
paths may lead to the same action, but multiple actions cannot directly share a
path. Instead, the action for one path may include a conditional redirect for
another path. Any views that require the user to be authenticated have the
@login_required decorator to automatically redirect unauthenticated users to
login view. Form validation is handled by WTForms and sessions management is
handled by Flask-Login, but it is still necessary to properly verify any user
provided data, particularly when it will be passed to an object that interacts
with the SPARQL endpoint.

Functions:
add_tag -- Create a new tag to store with the SPARQL endpoint.
load_user -- Retrieve a user from the triplestore for login authentication.
login -- Authenticate and create a session for a valid user.
logout -- Clear the session for a logged in user.
page_not_found -- Handle user attempts to access an invalid path.
show_tags -- Display the tags that have been defined and stored.
show_users -- List existing users and allow new users to be created.
"""

from flask import render_template, request, redirect, url_for, flash
#from flask_wtf import csrf
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, login_required, login_user, \
                            logout_user, current_user

from skmf import app, forms, g
from skmf.resource import User
import skmf.i18n.en_US as uiLabel

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/')
@app.route('/index')
def show_tags():
    """Use results from a form to add a tag entry to the datastore."""
    entries = g.sparql.query_subject()
    form = forms.AddEntryForm()
    return render_template('show_tags.html', title=uiLabel.viewTagTitle,
                           entries=entries, form=form)


@app.route('/add', methods=['POST'])
@login_required
def add_tag():
    form = forms.AddEntryForm()
    if form.validate_on_submit():
        label = form.label.data
        desc = form.description.data
        flash(g.sparql.sparql_insert(label, desc))
    return redirect(url_for('show_tags'), form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.get(form.username.data)
        if not user:
            # Make invalid username take same time as wrong password
            # Note: this may open up a denial of service vulnerability; it may
            #        be better to use sleep(1) instead.
            bcrypt.generate_password_hash(form.password.data)
            error = uiLabel.viewLoginInvalid
        elif not bcrypt.check_password_hash(user.get_hash(), form.password.data):
            error = uiLabel.viewLoginInvalid
        else:
            user.authenticated = True
            login_user(user)
            flash('{0!s} {1!s}'.format(uiLabel.viewLoginWelcome, user.name))
            return redirect(request.args.get('next') or url_for('show_tags'))
    return render_template('login.html', title=uiLabel.viewLoginTitle,
                           form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    flash(uiLabel.viewLogoutLoggedout)
    return redirect(url_for('show_tags'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def show_users():
    """Manage user information in the datastore."""
    form = forms.CreateUserForm()
    if form.is_submitted() and form.validate():
        user = User(form.username.data,
                    bcrypt.generate_password_hash(form.password.data))
        flash(user.get_hash())
#    entries = query_user()
    return render_template('show_users.html', title=uiLabel.viewUserTitle,
                           form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


#@csrf.error_handler
#def csrf_error(reason):
#    return render_template('csrf_error.html', reason=reason), 400


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
