# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Length(min=6, max=35)])
    # password = PasswordField('Password', validators=[DataRequired()])
    # remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login In')

