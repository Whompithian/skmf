"""skmf.forms by Brendan Sweeney, CSS 593, 2015.

WTForms definitions for use in Flask views. These forms may be passed from a
view into the call to render a template. The rendered template must provide an
interface to the form and must include the hidden_tag attribute of the passed
form from the context. Without this attribute, form submission will be ingored
under the assumption of a cross-site request forgery attempt. All fields of a
form, even those not visible to the user, are accessible to the calling view.
High-level field validation and sanitization are handled by the forms, but this
does not exempt the caller from properly validating any user-provided input.

Classes:
    AddConnectionForm: Form for creating RDF triples for existing resources.
    AddEntryForm: Form for adding a new general entry in the SPARQL endpoint.
    CreateUserForm: Form for adding a new user in the SPARQL endpoint.
    FindEntryForm: Form for searching for RDF triples based on some criteria.
    LoginForm: Form for users to authenticate from a Web page.
"""

from flask_wtf import Form
from wtforms import PasswordField, RadioField, SelectField, StringField, \
                    SubmitField, TextAreaField, validators

import skmf.i18n.en_US as uiLabel

MIN_PASS_LEN = 8
"""int: Minimum length to allow for user passwords."""

CAT_RESOURCE = 'skmf:Resource'
"""str: Prefix for content of type Resource."""

CAT_PROPERTY = 'rdf:Property'
"""str: Prefix for content of type Property."""


class LoginForm(Form):
    """Collect information to authenticate a user from a Web page.
    
    The form is valid only if both username and password are provided before it
    is submitted. Password length should not need to be validated here because
    legitimate users are expected to remember the length of their passwords. It
    Is up to the callig view to determine the legitimacy of the provided pass-
    word.
    
    Attributes:
        password: An obscured field to collect an existing user's password.
        submit: A button to submit the rendered form.
        username: A text field to collect an existing user's unique id.
    """

    username = StringField(
        label=uiLabel.formLoginUserTitle,
        validators=[validators.InputRequired(
            message=uiLabel.formLoginUserError)])

    password = PasswordField(
        label=uiLabel.formLoginPassTitle,
        validators=[validators.InputRequired(
            message=uiLabel.formLoginPassError)])

    submit = SubmitField(label=uiLabel.formLoginSubTitle)


class FindEntryForm(Form):
    """Retrieve information that was stored through the SPARQL endpoint.
    
    Query terms are selected, either by choosing them from a dropdown list or
    by entering a label in a text field. The dropdown list takes priority, so
    if both options are provided, only the dropdown value will be selected. Two
    sets of input fields are provided to allow for basic relationships to be
    queried, although this would ideally be done with a dynamically expanding
    form that can collect an arbitrary number of relationships from the user.
    Such functionality ought to be provided in the future.
    
    Attributes:
        connection: A dropdown list to select a property.
        connection_2: A dropdown list to select an optional property.
        free_conn: A text field to enter a label for a property.
        free_conn_2: A text field to enter a label for an optional property.
        free_res: A text field to enter a label for a resource.
        free_res_2: A text field to enter a label for an optional resource.
        free_target: A text field to enter a label or a value.
        free_target_2: A text field to enter an optional label or value.
        resource: A dropdown list to select a resource.
        resource_2: A dropdown list to select an optional resource.
        submit: A button to submit the rendered form.
        target: A dropdown list to select a value.
        target_2: A dropdown list to select an optional value.
    """

    resource = SelectField(
        label=uiLabel.formEntryResTitle,
        default='',
        validators=[validators.NoneOf(
            (' ', '-'), message=uiLabel.formEntrySelectResError)])

    connection = SelectField(
        label=uiLabel.formEntryConnTitle,
        default='',
        validators=[validators.NoneOf(
            (' ', '-'), message=uiLabel.formEntrySelectConError)])

    target = SelectField(
        label=uiLabel.formEntryTargetTitle,
        default='',
        validators=[validators.NoneOf(
            (' ', '-'), message=uiLabel.formEntrySelectTgtError)])

    free_res = StringField(label=uiLabel.formEntryResFreeTitle)

    free_conn = StringField(label=uiLabel.formEntryConnFreeTitle)

    free_target = StringField(label=uiLabel.formEntryTgtFreeTitle)

    resource_2 = SelectField(
        label=uiLabel.formEntryResTitle,
        default='',
        validators=[validators.NoneOf(
            (' ', '-'), message=uiLabel.formEntrySelectResError)])

    connection_2 = SelectField(
        label=uiLabel.formEntryConnTitle,
        default='',
        validators=[validators.NoneOf(
            (' ', '-'), message=uiLabel.formEntrySelectConError)])

    target_2 = SelectField(
        label=uiLabel.formEntryTargetTitle,
        default='',
        validators=[validators.NoneOf(
            (' ', '-'), message=uiLabel.formEntrySelectTgtError)])

    free_res_2 = StringField(label=uiLabel.formEntryResFreeTitle)

    free_conn_2 = StringField(label=uiLabel.formEntryConnFreeTitle)

    free_target_2 = StringField(label=uiLabel.formEntryTgtFreeTitle)

    submit = SubmitField(label=uiLabel.formEntrySubFindTitle)


class AddEntryForm(Form):
    """Collect information to be stored through the SPARQL endpoint.
    
    Three pieces of information are used to create new components in the data-
    store: a category, a label, and a description. The category specifies
    whether to treat the new component as a resource or as a property of a
    resource. The label determines the name of the new component and is used to
    check for collision with existing components. The description provides
    helpful text about the new resource.
    
    Attributes:
        category: A radio field to select the type of component to add.
        description: A text field to enter a detailed description.
        label: A text field to enter a concise label.
        submit: A button to submit the rendered form.
    """

    category = RadioField(
        label=uiLabel.formEntryCatTitle,
        default = CAT_RESOURCE,
        choices = [(CAT_RESOURCE, uiLabel.formEntryCatRes),
                   (CAT_PROPERTY, uiLabel.formEntryCatConn)])

    label = StringField(
        label=uiLabel.formEntryLabelTitle,
        validators=[validators.InputRequired(
            message=uiLabel.formEntryLabelError)])

    description = TextAreaField(
        label=uiLabel.formEntryDescTitle,
        validators=[validators.InputRequired(
            message=uiLabel.formEntryDescError)])

    submit = SubmitField(label=uiLabel.formEntrySubTitle)


class AddConnectionForm(Form):
    """Collect a triple of information to insert into the SPARQL endpoint.
    
    Currently, only existing components may be selected for the subject and
    predicate. The free-form text box should only be used to provide literals
    for the object value. URIs should be selected from the dropdown. This form
    does not link to any UPDATE functionality, so new triples will be placed
    next to existing triples rather than changing the object of an existing
    triple.
    
    Attributes:
        connection: A dropdown list to select a property.
        free_target: A text field to enter a label or a value.
        resource: A dropdown list to select a resource.
        submit: A button to submit the rendered form.
        target: A dropdown list to select a value.
    """

    resource = SelectField(
        label=uiLabel.formEntryResTitle,
        default='',
        validators=[
            validators.NoneOf((' ', '-'),
                              message=uiLabel.formEntrySelectResError),
            validators.InputRequired(message=uiLabel.formEntryLabelError)])

    connection = SelectField(
        label=uiLabel.formEntryConnTitle,
        default='',
        validators=[
            validators.NoneOf((' ', '-'),
                              message=uiLabel.formEntrySelectConError),
            validators.InputRequired(message=uiLabel.formEntryLabelError)])

    target = SelectField(
        label=uiLabel.formEntryTargetTitle,
        default='',
        validators=[
            validators.NoneOf((' ', '-'),
                              message=uiLabel.formEntrySelectTgtError)])

    free_target = TextAreaField(label=uiLabel.formEntryTgtFreeTitle)

    submit = SubmitField(label=uiLabel.formEntrySubAddTitle)


class CreateUserForm(Form):
    """Collect information from which to create a new user.
    
    The form is only valid if all fields are filled before it is submitted. In
    addition, the password and confirm fields must match and must contain at
    least MIN_PASS_LEN characters. It is up to the colling view to ensure that
    the specified user does not already exist before creating it.
    
    Attributes:
        confirm: A second password field to prevent a mistyped password.
        password: An obscured field to collect the password for a new user.
        submit: A button to submit the rendered form.
        username: A text field to collect the unique id of a new user.
    """

    username = StringField(
        label=uiLabel.formCreateUserUserTitle,
        validators=[
            validators.InputRequired(message=uiLabel.formCreateUserUserError)])

    password = PasswordField(
        label=uiLabel.formCreateUserPassTitle,
        validators=[
            validators.InputRequired(message=uiLabel.formCreateUserPassError),
            validators.Length(min=MIN_PASS_LEN,
                              message='{0!s} {1!s} {2!s}'.format(
                                  uiLabel.formCreateUserLenError1,
                                  MIN_PASS_LEN,
                                  uiLabel.formCreateUserLenError2))])

    confirm = PasswordField(
        label=uiLabel.formCreateUserConfTitle,
        validators=[
            validators.InputRequired(),
            validators.EqualTo('password',
                               message=uiLabel.formCreateUserConfError)])

    submit = SubmitField(label=uiLabel.formCreateUserSubTitle)
