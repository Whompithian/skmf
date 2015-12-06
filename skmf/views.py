"""skmf.views by Brendan Sweeney, CSS 593, 2015.

Define the views that are rendered by Flask to the end user. This controls what
action to take given a URL path provided by the user. Typically, a path will
result in the display of a Web page which is rendered from a template. Multiple
paths may lead to the same action, but multiple actions cannot directly share a
path. Instead, the action for one path may include a conditional redirect for
another path. Any views that require the user to be authenticated have the
@login_required decorator to automatically redirect unauthenticated users to a
login view. Form validation is handled by WTForms and session management is
handled by Flask-Login, but it is still necessary to properly verify any user
provided data, particularly when it will be passed to an object that interacts
with the SPARQL endpoint.

Functions:
    add_conn: Insert one RDF triple through the SPARQL endpoint.
    add_tag: Create a new tag to store with the SPARQL endpoint.
    add_user: Create a new user to store with the SPARQL endpoint.
    load_user: Retrieve a user from the triplestore for login authentication.
    login: Authenticate and create a session for a valid user.
    logout: Clear the session for a logged in user.
    page_not_found: Handle user attempts to access an invalid path.
    resources: View and manage resources in the datastore.
    show_subject: Display all triples for a single RDF subject.
    welcome: Display a basic landing page.
"""

from time import sleep

from flask import render_template, request, redirect, url_for, flash
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager, login_required, login_user, \
                            logout_user, current_user

from skmf import app, forms
from skmf.resource import Query, Subject, User
import skmf.i18n.en_US as uiLabel

bcrypt = Bcrypt(app)
"""Password hash management for secure user sessions and persistence."""

login_manager = LoginManager()
"""User session manager and token handler."""
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/')
@app.route('/index')
def welcome():
    """Display a landing page with pointers on getting started with SKMF."""
    return render_template('welcome.html', title=uiLabel.viewWelcomeTitle)


@app.route('/resources', methods=['GET', 'POST'])
def resources():
    """View and manage resources in the datastore.
    
    This function is only meant to provide a basic demonstration of the under-
    lying SPARQL functionality. It is barely functional and is a mess of
    functionality that needs to be split into multiple views. That said, it
    allows a user to: perform queries with one degree of separation from the
    target; create resources and connections (properties) in the datastore;
    insert triples involving existing resources and connections into the data-
    store. Ideally, this functionality will be migrated to a set of views that
    are capable of providing the same level of dynamic query building as is
    supported by the backend.
    
    Returns:
        Rendered page containing forms and query results, if any.
    """
    entries = None
    print('entering entries')
    # Failure to set explicit parameters leads to broken garbage collection
    query = Query(labellist = set(), subjectlist = {}, optlist = [])
    print('empty query')
    rdfs_class = query.get_resources('rdfs:Class')
    owl_class = query.get_resources('owl:Class')
    owl_obj_prop = query.get_resources('owl:ObjectProperty')
    owl_dtype_prop = query.get_resources('owl:DatatypeProperty')
    rdf_property = query.get_resources('rdf:Property')
    skmf_resource = query.get_resources('skmf:Resource')
    print('resources gathered')
    query_form = forms.FindEntryForm()
    print('empty FindEntryForm')
    res_choices = set()
    for res in skmf_resource:
        if res['resource']['type'] != 'bnode':
            res_choices.add((res['resource']['value'],
                          res['label']['value'] if 'value' in res['label'] else res['resource']['value'].partition('#')[2]))
    res_sorted = sorted(list(res_choices), key=lambda x: x[1])
    conn_choices = set()
    for conn in rdf_property:
        if conn['resource']['type'] != 'bnode':
            conn_choices.add((conn['resource']['value'],
                        conn['label']['value'] if 'value' in conn['label'] else conn['resource']['value'].partition('#')[2]))
    for conn in owl_obj_prop:
        if conn['resource']['type'] != 'bnode':
            conn_choices.add((conn['resource']['value'],
                        conn['label']['value'] if 'value' in conn['label'] else conn['resource']['value'].partition('#')[2]))
    for conn in owl_dtype_prop:
        if conn['resource']['type'] != 'bnode':
            conn_choices.add((conn['resource']['value'],
                        conn['label']['value'] if 'value' in conn['label'] else conn['resource']['value'].partition('#')[2]))
    conn_choices.add(('http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'A'))
    conn_sorted = sorted(list(conn_choices), key=lambda x: x[1])
    targ_choices = set()
    for targ in rdfs_class:
        if targ['resource']['type'] != 'bnode':
            targ_choices.add((targ['resource']['value'],
                        targ['label']['value'] if 'value' in targ['label'] else targ['resource']['value'].partition('#')[2]))
    for targ in owl_class:
        if targ['resource']['type'] != 'bnode':
            targ_choices.add((targ['resource']['value'],
                        targ['label']['value'] if 'value' in targ['label'] else targ['resource']['value'].partition('#')[2]))
    targ_sorted = sorted(list(targ_choices), key=lambda x: x[1])
    print('resources sorted')
    query_form.resource.choices = res_sorted[:]
    query_form.resource.choices.insert(0, (' ', ''))
    query_form.resource.choices.insert(0, ('-', '---'))
    query_form.resource.choices.insert(0, ('', 'Resource'))
    query_form.connection.choices = conn_sorted[:]
    query_form.connection.choices.insert(0, (' ', ''))
    query_form.connection.choices.insert(0, ('-', '---'))
    query_form.connection.choices.insert(0, ('', 'Connection'))
    query_form.target.choices = targ_sorted[:]
    query_form.target.choices.insert(0, (' ', ''))
    query_form.target.choices.insert(0, ('-', '---'))
    query_form.target.choices.insert(0, ('', 'Target'))
    query_form.resource_2.choices = res_sorted[:]
    query_form.resource_2.choices.insert(0, (' ', ''))
    query_form.resource_2.choices.insert(0, ('-', '---'))
    query_form.resource_2.choices.insert(0, ('', 'Resource'))
    query_form.connection_2.choices = conn_sorted[:]
    query_form.connection_2.choices.insert(0, (' ', ''))
    query_form.connection_2.choices.insert(0, ('-', '---'))
    query_form.connection_2.choices.insert(0, ('', 'Connection'))
    query_form.target_2.choices = targ_sorted[:]
    query_form.target_2.choices.insert(0, (' ', ''))
    query_form.target_2.choices.insert(0, ('-', '---'))
    query_form.target_2.choices.insert(0, ('', 'Target'))
    print('FindEntryForm populated')
    insert_form = forms.AddEntryForm()
    print('empty AddEntryForm')
    update_form = forms.AddConnectionForm()
    print('empty AddConnectionForm')
    update_form.resource.choices = res_sorted[:]
    update_form.resource.choices.insert(0, (' ', ''))
    update_form.resource.choices.insert(0, ('-', '---'))
    update_form.resource.choices.insert(0, ('', 'Resource'))
    update_form.connection.choices = conn_sorted[:]
    update_form.connection.choices.insert(0, (' ', ''))
    update_form.connection.choices.insert(0, ('-', '---'))
    update_form.connection.choices.insert(0, ('', 'Connection'))
    update_form.target.choices = targ_sorted[:]
    update_form.target.choices.insert(0, (' ', ''))
    update_form.target.choices.insert(0, ('-', '---'))
    update_form.target.choices.insert(0, ('', 'Target'))
    print('AddConnectionForm populated')
    if query_form.validate_on_submit():
        print('wrong form submitted')
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
#    if update_form.validate_on_submit():
#        resource = Subject(update_form.resource.data)
#        property = update_form.connection.data
#        value = update_form.target.data
#        object_type = 'uri'
#        lang = ''
#        if not value:
#            value = update_form.free_object.data
#            object_type = 'literal'
#            lang = uiLabel.ISOCode.lower()
#        rdf_object = {}
#        rdf_object['value'] = value
#        rdf_object['type'] = object_type
#        if lang:
#            rdf_object['xml:lang'] = lang
#        pred_value = {}
#        pred_value['type'] = 'uri'
#        pred_value['value'] = [rdf_object]
#        pred_list = {}
#        pred_list[property] = pred_value
#        resource.add_data(graphlist={''}, predlist=pred_list)
    return render_template('resources.html', title=uiLabel.viewTagTitle,
                           entries=entries, query_form=query_form,
                           insert_form=insert_form, update_form=update_form)


@app.route('/add', methods=['POST'])
@login_required
def add_tag():
    """Add a Resource or Connection to the datastore.
    
    A Resource is a special class that will come up as the option for subjects
    in query form dropdown lists. A Connection is any rdf:Property, also often
    added to query form dropdown lists. A label and description are required to
    maintain some consistency in the datastore and to ensure that users are
    able to understand what has been returned by a query.
    
    Returns:
        Redirect to the resource management Web page.
    """
    insert_form = forms.AddEntryForm()
    if insert_form.validate_on_submit():
        insert_query = Query(labellist = set(), subjectlist = {}, optlist = [])
        cat = insert_form.category.data
        label = insert_form.label.data
        desc = insert_form.description.data
        lang = uiLabel.ISOCode.lower()
        insert_query.add_resource(cat, label, desc, lang)
    return redirect(url_for('resources'))


@app.route('/insert', methods=['POST'])
@login_required
def add_conn():
    """Add a connection to an existing resource in the datastore.
    
    This view is not used, as its functionality was placed directly in the
    'resources' view because that view already had the query needed to fill the
    options for the dropdown lists. In the future, that functionality should be
    returned to this function to clean up the code.
    
    Returns:
        Redirect to the resource management Web page.
    """
    # Failure to set explicit parameters leads to broken garbage collection
    query = Query(labellist = set(), subjectlist = {}, optlist = [])
    rdfs_class = query.get_resources('rdfs:Class')
    owl_class = query.get_resources('owl:Class')
    owl_obj_prop = query.get_resources('owl:ObjectProperty')
    owl_dtype_prop = query.get_resources('owl:DatatypeProperty')
    rdf_property = query.get_resources('rdf:Property')
    skmf_resource = query.get_resources('skmf:Resource')
    res_choices = set()
    for res in skmf_resource:
        if res['resource']['type'] != 'bnode':
            res_choices.add((res['resource']['value'],
                          res['label']['value'] if 'value' in res['label'] else res['resource']['value'].partition('#')[2]))
    res_sorted = sorted(list(res_choices), key=lambda x: x[1])
    conn_choices = set()
    for conn in rdf_property:
        if conn['resource']['type'] != 'bnode':
            conn_choices.add((conn['resource']['value'],
                        conn['label']['value'] if 'value' in conn['label'] else conn['resource']['value'].partition('#')[2]))
    for conn in owl_obj_prop:
        if conn['resource']['type'] != 'bnode':
            conn_choices.add((conn['resource']['value'],
                        conn['label']['value'] if 'value' in conn['label'] else conn['resource']['value'].partition('#')[2]))
    for conn in owl_dtype_prop:
        if conn['resource']['type'] != 'bnode':
            conn_choices.add((conn['resource']['value'],
                        conn['label']['value'] if 'value' in conn['label'] else conn['resource']['value'].partition('#')[2]))
    conn_choices.add(('http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'A'))
    conn_sorted = sorted(list(conn_choices), key=lambda x: x[1])
    targ_choices = set()
    for targ in rdfs_class:
        if targ['resource']['type'] != 'bnode':
            targ_choices.add((targ['resource']['value'],
                        targ['label']['value'] if 'value' in targ['label'] else targ['resource']['value'].partition('#')[2]))
    for targ in owl_class:
        if targ['resource']['type'] != 'bnode':
            targ_choices.add((targ['resource']['value'],
                        targ['label']['value'] if 'value' in targ['label'] else targ['resource']['value'].partition('#')[2]))
    targ_sorted = sorted(list(targ_choices), key=lambda x: x[1])
    update_form = forms.AddConnectionForm()
    update_form.resource.choices = res_sorted[:]
    update_form.resource.choices.insert(0, (' ', ''))
    update_form.resource.choices.insert(0, ('-', '---'))
    update_form.resource.choices.insert(0, ('', 'Resource'))
    update_form.connection.choices = conn_sorted[:]
    update_form.connection.choices.insert(0, (' ', ''))
    update_form.connection.choices.insert(0, ('-', '---'))
    update_form.connection.choices.insert(0, ('', 'Connection'))
    update_form.target.choices = targ_sorted[:]
    update_form.target.choices.insert(0, (' ', ''))
    update_form.target.choices.insert(0, ('-', '---'))
    update_form.target.choices.insert(0, ('', 'Target'))
    if update_form.validate_on_submit():
        print('update_form validated')
        resource = Subject(update_form.resource.data)
        property = update_form.connection.data
        value = update_form.target.data
        object_type = 'uri'
        lang = ''
        if not value:
            value = update_form.free_target.data
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
    return redirect(url_for('resources'))


@app.route('/retrieve')
def show_subject():
    """Query and display all triples pertaining to a singel subject.
    
    If a user is not able to refine a query to retrieve relevant information,
    it is always possible to look at all information pertaining to a single
    subject. Access to this information may even help the user devise a better
    query.
    
    Returns:
        Rendered page containing all predicates and objects for one subject.
    """
    subject = Subject(request.args.get('subject'))
    return render_template('show_subject.html',
                           title=subject.id, preds=subject.preds)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Setup a user session.
    
    A user is retrieved based on the user ID entered in the login form. It the
    user does not exist, a small time is passed to throw off timing attacks.
    Otherwise, the password is collected from the Web form and its BCrypt hash
    compared to the hash of the retrieved user. A match results in successful
    authentication. All other conditions result in an error.
    
    Returns:
        Login page if not authenticated, resource management page otherwise.
    """
    error = None
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.get(form.username.data)
        if not user:
            # Make invalid username take same time as wrong password
            sleep(1.3)
            error = uiLabel.viewLoginInvalid
        elif not bcrypt.check_password_hash(user.get_hash(),
                                            form.password.data):
            error = uiLabel.viewLoginInvalid
        else:
            user.authenticated = True
            login_user(user)
            flash('{0!s} {1!s}'.format(uiLabel.viewLoginWelcome,
                                       user.get_name()))
            return redirect(request.args.get('next') or url_for('resources'))
    return render_template('login.html', title=uiLabel.viewLoginTitle,
                           form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    """End a user session.
    
    The current user is set to unauthenticated and session tokens are dropped.
    
    Returns:
        Redirect to the resource management Web page.
    """
    user = current_user
    user.authenticated = False
    logout_user()
    flash(uiLabel.viewLogoutLoggedout)
    return redirect(url_for('resources'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def add_user():
    """Manage user information in the datastore.
    
    Currently, users may be added and their passwords set. There is no way to
    remove a user, set a display name, add permission to the 'users' graph, or
    change a password. Also, username is permanent for any user.
    
    Returns:
        'Add User' page if current user is 'admin', resource page otherwise.
    """
    if current_user.get_id() != 'admin':
        return redirect(url_for('resources'))
    form = forms.CreateUserForm()
    if form.validate_on_submit():
        user = User(form.username.data)
        if not user.preds:
            user.set_hash(bcrypt.generate_password_hash(form.password.data))
            user.set_active()
        else:
            flash('User already exists')
    return render_template('users.html', title=uiLabel.viewUserTitle,
                           form=form)


@app.errorhandler(404)
def page_not_found(error):
    """Handle attempts to access nonexistent pages."""
    return render_template('page_not_found.html'), 404


@login_manager.user_loader
def load_user(user_id):
    """Create an instance of the User from the datastore, if id is found."""
    return User.get(user_id)
