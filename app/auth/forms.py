# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo



class RegisterForm(FlaskForm):
    email = StringField('', validators=[DataRequired(message="请输入邮箱地址"),
                                        Length(1, 64),
                                        Email(message="必须是合法的邮箱地址")])
    username = StringField('', validators=[DataRequired(message="请输入用户名"),
                                           Length(1, 10), Regexp(
                                        '^[A-Za-z][A-Za-z0-9_]*$', flags=0,
                                        message="用户名必须是数字、字母或下划线的组合")])
    password = PasswordField('', validators=[
        DataRequired(), EqualTo('password2', message='两次密码输入不一致')])
    password2 = PasswordField('', validators=[DataRequired()])
