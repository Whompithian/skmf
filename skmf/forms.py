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
    AddEntryForm: Form for adding a new general entry in the SPARQL endpoint.
    CreateUserForm: Form for adding a new user in the SPARQL endpoint.
    LoginForm: Form for users to authenticate from a Web page.
"""

from flask_wtf import Form
from wtforms import PasswordField, RadioField, SelectField, StringField, SubmitField, TextAreaField, validators
#from wtforms.widgets import Select#, TableWidget

import skmf.i18n.en_US as uiLabel

MIN_PASS_LEN = 8
"""Minimum length to allow for user passwords."""


class LoginForm(Form):
    """Collect information to authenticate a user from a Web page.
    
    The form is valid only if both username and password are provided before it
    is submitted. Password length should not need to be validated here because
    legitimate users are expected to remember the length of their passwords.
    It is up to the callig view to determine the legitimacy of the provided
    password.
    
    Attributes:
        password -- An obscured field to collect an existing user's password.
        submit -- A button to submit the rendered form.
        username -- A text field to collect an existing user's unique id.
    """

    username = StringField(uiLabel.formLoginUserTitle,
            [validators.InputRequired(message=uiLabel.formLoginUserError)])
    password = PasswordField(uiLabel.formLoginPassTitle,
            [validators.InputRequired(message=uiLabel.formLoginPassError)])
    submit = SubmitField(uiLabel.formLoginSubTitle)


class FindEntryForm(Form):
    """Retrieve information that was stored through the SPARQL endpoint.
    
    This form should dynamically expand as the user selects more options.
            It may turn out to be much more complex.
    """
    connection = SelectField(label=uiLabel.formEntryConnTitle, default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    resource = SelectField(label=uiLabel.formEntryResTitle, default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    target = SelectField(label='Target', default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    free_conn = StringField(label='Free-form connection')
    free_res = StringField(label='Free-form resource')
    free_target = StringField(label='Free-form target')
    connection_2 = SelectField(label=uiLabel.formEntryConnTitle, default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    resource_2 = SelectField(label=uiLabel.formEntryResTitle, default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    target_2 = SelectField(label='Target', default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    free_conn_2 = StringField(label='Free-form connection')
    free_res_2 = StringField(label='Free-form resource')
    free_target_2 = StringField(label='Free-form target')
    submit = SubmitField(label='Retrieve')


class AddEntryForm(Form):
    """Collect information to be stored through the SPARQL endpoint.
    
    This form should dynamically expand as the user selects more options.
            It may turn out to be much more complex.
    """

    category = RadioField(label=uiLabel.formEntryCatTitle,
                          default = 'skmf:Resource',
                          choices = [('skmf:Resource',
                                      uiLabel.formEntryCatRes),
                                     ('rdf:Property',
                                      uiLabel.formEntryCatConn)
                                     ])
    label = StringField(label=uiLabel.formEntryLabelTitle, validators=
            [validators.InputRequired(message=uiLabel.formEntryLabelError)])
    description = TextAreaField(label=uiLabel.formEntryDescTitle, validators=
            [validators.InputRequired(message=uiLabel.formEntryDescError)])
    submit = SubmitField(label=uiLabel.formEntrySubTitle)


class AddConnectionForm(Form):
    """Collect a triple of information to insert into the SPARQL endpoint."""
    rdf_subject = SelectField(label='Resource', default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    rdf_pred = SelectField(label='Property', default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    rdf_object = SelectField(label='Value', default='',
            validators=[validators.NoneOf((' ', '-'), message='Fail!')])
    free_object = TextAreaField(label='Free-form value')
    submit = SubmitField(label='Insert')


class CreateUserForm(Form):
    """Collect information from which to create a new user.
    
    The form is only valid if all fields are filled before it is submitted. In
    addition, the password and confirm fields must match and must contain at
    least MIN_PASS_LEN characters. It is up to the colling view to ensure that
    the specified user does not already exist before creating it.
    
    Attributes:
        confirm -- A second password field to prevent a mistyped password.
        password -- An obscured field to collect the password for a new user.
        submit -- A button to submit the rendered form.
        username -- A text field to collect the unique id of a new user.
    """

    username = StringField(uiLabel.formCreateUserUserTitle,
            [validators.InputRequired(message=uiLabel.formCreateUserUserError)])
    password = PasswordField(uiLabel.formCreateUserPassTitle,
            [validators.InputRequired(message=uiLabel.formCreateUserPassError),
            validators.Length(min=MIN_PASS_LEN,
                    message='{0!s} {1!s} {2!s}'.format(
                            uiLabel.formCreateUserLenError1,
                            MIN_PASS_LEN,
                            uiLabel.formCreateUserLenError2))])
    confirm = PasswordField(uiLabel.formCreateUserConfTitle,
            [validators.InputRequired(),
            validators.EqualTo('password',
                               message=uiLabel.formCreateUserConfError)])
    submit = SubmitField(uiLabel.formCreateUserSubTitle)
