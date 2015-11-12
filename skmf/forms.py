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
AddEntryForm -- Form for adding a new general entry in the SPARQL endpoint.
CreateUserForm -- Form for adding a new user in the SPARQL endpoint.
LoginForm -- Form for users to authenticate from a Web page.
"""

from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField, validators

import skmf.i18n.en_US as uiLabel

MIN_PASS_LEN = 8


class LoginForm(Form):
    username = StringField(uiLabel.formLoginUserTitle,
            [validators.InputRequired(message=uiLabel.formLoginUserError)])
    password = PasswordField(uiLabel.formLoginPassTitle,
            [validators.InputRequired(message=uiLabel.formLoginPassError)])
    submit = SubmitField(uiLabel.formLoginSubTitle)


class AddEntryForm(Form):
    label = StringField(uiLabel.formEntryLabelTitle,
            [validators.InputRequired(message=uiLabel.formEntryLabelError)])
    description = StringField(uiLabel.formEntryDescTitle,
            [validators.InputRequired(message=uiLabel.formEntryDescError)])
    submit = SubmitField(uiLabel.formEntrySubTitle)


class CreateUserForm(Form):
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
