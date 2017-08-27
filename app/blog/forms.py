# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, FileField
from flask_pagedown.fields import PageDownField
from wtforms.validators import Length, DataRequired, Email


# Post a new blog article form
class WriteForm(FlaskForm):
    picture = FileField('Picture limited 10MB', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Image only!')
    ])
    title = StringField('Title', validators=[DataRequired(), Length(1, 100)])
    subtitle = StringField('Subtitle', validators=[Length(0, 120)])
    brief_title = StringField('Brief Title',
                              validators=[DataRequired(), Length(1, 240)])
    tags = StringField('Tags (split with ";" every tag limited char 10)')
    body = PageDownField('Body Content: (PS. support markdown)')
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    content = PageDownField('', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentOpenForm(FlaskForm):
    open_content = PageDownField('留言', validators=[DataRequired()])
    open_name = StringField("姓名", validators=[DataRequired()])
    open_email = StringField("邮箱", validators=[DataRequired(), Email()])
    open_submit = SubmitField("提交")
