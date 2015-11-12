from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField, validators

import skmf.i18n.en_US as lang

MIN_PASS_LEN = 8


class LoginForm(Form):
    username = StringField(lang.formLoginUserTitle,
            [validators.InputRequired(message=lang.formLoginUserError)])
    password = PasswordField(lang.formLoginPassTitle,
            [validators.InputRequired(message=lang.formLoginPassError)])
    submit = SubmitField(lang.formLoginSubTitle)


class CreateUserForm(Form):
    username = StringField(lang.formCreateUserUserTitle,
            [validators.InputRequired(message=lang.formCreateUserUserError)])
    password = PasswordField(lang.formCreateUserPassTitle,
            [validators.InputRequired(message=lang.formCreateUserPassError),
            validators.Length(min=MIN_PASS_LEN,
                    message='{0!s} {1!s} {2!s}'.format(
                            lang.formCreateUserLenError1,
                            MIN_PASS_LEN,
                            lang.formCreateUserLenError2))])
    confirm = PasswordField(lang.formCreateUserConfTitle,
            [validators.InputRequired(),
            validators.EqualTo('password',
                               message=lang.formCreateUserConfError)])
    submit = SubmitField(lang.formCreateUserSubTitle)
