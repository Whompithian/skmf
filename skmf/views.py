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
    add_tag: Create a new tag to store with the SPARQL endpoint.
    load_user: Retrieve a user from the triplestore for login authentication.
    login: Authenticate and create a session for a valid user.
    logout: Clear the session for a logged in user.
    page_not_found: Handle user attempts to access an invalid path.
    show_tags: Display the tags that have been defined and stored.
    show_users: List existing users and allow new users to be created.
"""

from time import sleep

from flask import render_template, request, redirect, url_for, flash
#from flask_wtf.csrf import CsrfProtect
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, login_required, login_user, \
                            logout_user, current_user

from skmf import app, forms#, g
from skmf.resource import Query, Subject, User
import skmf.i18n.en_US as uiLabel

bcrypt = Bcrypt(app)
#CsrfProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/')
@app.route('/index')
def welcome():
    """Display a landing page with pointers on getting started with SKMF."""
    return render_template('welcome.html', title='Welcome')


@app.route('/resources', methods=['GET', 'POST'])
def show_tags():
    """Use results from a form to add a tag entry to the datastore."""
    entries = None
    # Failure to set explicit parameters leads to broken garbage collection
    query = Query(labellist = set(), subjectlist = {}, optlist = [])
    rdfs_class = query.get_resources('rdfs:Class')
    rdf_property = query.get_resources('rdf:Property')
    skmf_resource = query.get_resources('skmf:Resource')
    query_form = forms.FindEntryForm()
    query_form.connection.choices = [(c['resource']['value'], c['label']['value']) for c in rdf_property]
    query_form.connection.choices.insert(0, (' ', ''))
    query_form.connection.choices.insert(0, ('-', '---'))
    query_form.connection.choices.insert(0, ('', 'Connection'))
    query_form.resource.choices = [(r['resource']['value'], r['label']['value']) for r in skmf_resource]
    query_form.resource.choices.insert(0, (' ', ''))
    query_form.resource.choices.insert(0, ('-', '---'))
    query_form.resource.choices.insert(0, ('', 'Resource'))
    query_form.target.choices = [(r['resource']['value'], r['label']['value']) for r in rdfs_class]
    query_form.target.choices.insert(0, (' ', ''))
    query_form.target.choices.insert(0, ('-', '---'))
    query_form.target.choices.insert(0, ('', 'Target'))
    query_form.connection_2.choices = [(c['resource']['value'], c['label']['value']) for c in rdf_property]
    query_form.connection_2.choices.insert(0, (' ', ''))
    query_form.connection_2.choices.insert(0, ('-', '---'))
    query_form.connection_2.choices.insert(0, ('', 'Connection'))
    query_form.resource_2.choices = [(r['resource']['value'], r['label']['value']) for r in skmf_resource]
    query_form.resource_2.choices.insert(0, (' ', ''))
    query_form.resource_2.choices.insert(0, ('-', '---'))
    query_form.resource_2.choices.insert(0, ('', 'Resource'))
    query_form.target_2.choices = [(r['resource']['value'], r['label']['value']) for r in rdfs_class]
    query_form.target_2.choices.insert(0, (' ', ''))
    query_form.target_2.choices.insert(0, ('-', '---'))
    query_form.target_2.choices.insert(0, ('', 'Target'))
    insert_form = forms.AddEntryForm()
    update_form = forms.AddConnectionForm()
    update_form.rdf_subject.choices = [(c['resource']['value'], c['label']['value']) for c in skmf_resource]
    update_form.rdf_subject.choices.insert(0, (' ', ''))
    update_form.rdf_subject.choices.insert(0, ('-', '---'))
    update_form.rdf_subject.choices.insert(0, ('', 'Resource'))
    update_form.rdf_pred.choices = [(r['resource']['value'], r['label']['value']) for r in rdf_property]
    update_form.rdf_pred.choices.insert(0, (' ', ''))
    update_form.rdf_pred.choices.insert(0, ('-', '---'))
    update_form.rdf_pred.choices.insert(0, ('', 'Connection'))
    update_form.rdf_object.choices = [(r['resource']['value'], r['label']['value']) for r in rdfs_class]
    update_form.rdf_object.choices.insert(0, (' ', ''))
    update_form.rdf_object.choices.insert(0, ('-', '---'))
    update_form.rdf_object.choices.insert(0, ('', 'Target'))
    if query_form.validate_on_submit():
        if query_form.target.data:
            rdf_object = {}
            rdf_object['type'] = 'uri'
            rdf_object['value'] = query_form.target.data
        else:
            rdf_object = {}
            rdf_object['type'] = 'label'
            rdf_object['value'] = query_form.free_target.data
        if query_form.connection.data:
            rdf_pred = {}
            rdf_pred['type'] = 'uri'
            rdf_pred['value'] = query_form.connection.data
        else:
            rdf_pred = {}
            rdf_pred['type'] = 'label'
            rdf_pred['value'] = query_form.free_conn.data
        if query_form.resource.data:
            rdf_subject = {}
            rdf_subject['type'] = 'uri'
            rdf_subject['value'] = query_form.resource.data
        else:
            rdf_subject = {}
            rdf_subject['type'] = 'label'
            rdf_subject['value'] = query_form.free_res.data
        triples = []
        triple = {}
        triple['object'] = rdf_object
        triple['predicate'] = rdf_pred
        triple['subject'] = rdf_subject
        triples.append(triple)
        if query_form.target_2.data:
            rdf_object_2 = {}
            rdf_object_2['type'] = 'uri'
            rdf_object_2['value'] = query_form.target_2.data
        else:
            rdf_object_2 = {}
            rdf_object_2['type'] = 'label'
            rdf_object_2['value'] = query_form.free_target_2.data
        if query_form.connection_2.data:
            rdf_pred_2 = {}
            rdf_pred_2['type'] = 'uri'
            rdf_pred_2['value'] = query_form.connection_2.data
        else:
            rdf_pred_2 = {}
            rdf_pred_2['type'] = 'label'
            rdf_pred_2['value'] = query_form.free_conn_2.data
        if query_form.resource_2.data:
            rdf_subject_2 = {}
            rdf_subject_2['type'] = 'uri'
            rdf_subject_2['value'] = query_form.resource_2.data
        else:
            rdf_subject_2 = {}
            rdf_subject_2['type'] = 'label'
            rdf_subject_2['value'] = query_form.free_res_2.data
        triple_2 = {}
        triple_2['object'] = rdf_object_2
        triple_2['predicate'] = rdf_pred_2
        triple_2['subject'] = rdf_subject_2
        triples.append(triple_2)
        entries = []
        temp = query.get_entries(triples)
        for entry in temp:
            new_entry = {}
            for label in entry:
                if '_label' not in label:
                    item = {}
                    value = entry[label]['value']
                    item['value'] = value
                    if entry[label]['type'] == 'uri':
                        uri = value
                        item['uri'] = uri
                    if 'value' in entry['{}_label'.format(label)]:
                        tag = entry['{}_label'.format(label)]['value']
                        item['tag'] = tag
                    new_entry[label] = item
            entries.append(new_entry)
    if update_form.validate_on_submit():
        resource = Subject(update_form.rdf_subject.data)
        property = update_form.rdf_pred.data
        value = update_form.rdf_object.data
        object_type = 'uri'
        lang = ''
        if not value:
            value = update_form.free_object.data
            object_type = 'literal'
            lang = uiLabel.ISOCode.lower()
        rdf_object = {}
        rdf_object['value'] = value
        rdf_object['type'] = object_type
        if lang:
            rdf_object['xml:lang'] = lang
        pred_value = {}
        pred_value['type'] = 'uri'
        pred_value['value'] = [rdf_object]
        pred_list = {}
        pred_list[property] = pred_value
        resource.add_data(graphlist={''}, predlist=pred_list)
    return render_template('show_tags.html', title=uiLabel.viewTagTitle, entries=entries, query_form=query_form, insert_form=insert_form, update_form=update_form)


@app.route('/add', methods=['POST'])
@login_required
def add_tag():
    """Add a resource or connection to the datastore."""
    insert_form = forms.AddEntryForm()
    if insert_form.validate_on_submit():
        insert_query = Query(labellist = set(), subjectlist = {}, optlist = [])
        cat = insert_form.category.data
        label = insert_form.label.data
        desc = insert_form.description.data
        lang = uiLabel.ISOCode.lower()
        insert_query.add_resource(cat, label, desc, lang)
    return redirect(url_for('show_tags'))


@app.route('/insert', methods=['POST'])
@login_required
def add_conn():
    """Add a connection to an existing resource in the datastore."""
    update_form = forms.AddConnectionForm()
    if update_form.validate_on_submit():
        resource = Subject(update_form.rdf_subject.data)
        property = update_form.rdf_pred.data
        value = update_form.rdf_object.data
        object_type = 'uri'
        lang = ''
        if not value:
            value = update_form.free_object.data
            object_type = 'literal'
            lang = uiLabel.ISOCode.lower()
        rdf_object = {}
        rdf_object['value'] = value
        rdf_object['type'] = object_type
        if lang:
            rdf_object['xml:lang'] = lang
        pred_value = {}
        pred_value['type'] = 'uri'
        pred_value['value'] = [rdf_object]
        pred_list = {}
        pred_list[property] = pred_value
        resource.add_data(graphlist={''}, predlist=pred_list)
    return redirect(url_for('show_tags'))


@app.route('/retrieve')
def show_subject():
    subject = Subject(request.args.get('subject'))
#    general_query = Query()
#    connections = general_query.get_resources('Connection')
#    resources = general_query.get_resources('Resource')
#    query_form = forms.FindEntryForm()
#    query_form.connection.choices = [(c['resource']['value'], c['label']['value']) for c in connections]
#    query_form.resource.choices = [(r['resource']['value'], r['label']['value']) for r in resources]
#    if query_form.validate_on_submit():
#        label = query_form.label.data
#        desc = query_form.description.data
#        flash(g.sparql.sparql_insert(label, desc))
    return render_template('show_subject.html', title=subject.id, preds=subject.preds)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Setup a user session."""
    error = None
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.get(form.username.data)
        if not user:
            # Make invalid username take same time as wrong password
            sleep(1.3)
            error = uiLabel.viewLoginInvalid
        elif not bcrypt.check_password_hash(user.get_hash(), form.password.data):
            error = uiLabel.viewLoginInvalid
        else:
            user.authenticated = True
            login_user(user)
            flash('{0!s} {1!s}'.format(uiLabel.viewLoginWelcome, user.get_name()))
            return redirect(request.args.get('next') or url_for('show_tags'))
    return render_template('login.html', title=uiLabel.viewLoginTitle,
                           form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    """End a user session."""
    user = current_user
    user.authenticated = False
    logout_user()
    flash(uiLabel.viewLogoutLoggedout)
    return redirect(url_for('show_tags'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def add_user():
    """Manage user information in the datastore."""
    if current_user.get_id() != 'admin':
        return redirect(url_for('show_tags'))
    form = forms.CreateUserForm()
    if form.validate_on_submit():
        user = User(form.username.data)
        user.set_hash(bcrypt.generate_password_hash(form.password.data))
        user.set_active()
    return render_template('show_users.html', title=uiLabel.viewUserTitle,
                           form=form)


@app.errorhandler(404)
def page_not_found(error):
    """Handle attempts to access nonexistent pages."""
    return render_template('page_not_found.html'), 404


#@csrf.error_handler
#def csrf_error(reason):
#    return render_template('csrf_error.html', reason=reason), 400


@login_manager.user_loader
def load_user(user_id):
    """Create an instance of the User from the datastore, if id is found."""
    return User.get(user_id)
