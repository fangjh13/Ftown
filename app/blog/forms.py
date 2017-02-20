# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from flask_pagedown.fields import PageDownField
from wtforms.validators import Length, DataRequired

# Post a new blog article form
class WriteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 80)])
    subtitle = StringField('Subtitle', validators=[Length(0, 80)])
    body = PageDownField('Body Content: PS. support markdwon')
    submit = SubmitField('Submit', validators=[DataRequired()])