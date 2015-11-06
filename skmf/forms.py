from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField, validators


class LoginForm(Form):
    username = StringField('Username:', [validators.InputRequired(message='Username required')])
    password = PasswordField('Password:', [validators.InputRequired(message='Password required')])
    submit = SubmitField('Login')


class CreateUserForm(Form):
    username = StringField('Username:', [validators.InputRequired(message='Username required')])
    password = PasswordField('Password:', [validators.InputRequired(message='Password required')])
    confirm = PasswordField('Confirm password:', [validators.InputRequired(),
                                         validators.EqualTo(password, message='Passwords differ')])
    submit = SubmitField('Create')
