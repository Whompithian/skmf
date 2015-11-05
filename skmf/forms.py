from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')
