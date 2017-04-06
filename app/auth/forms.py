# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo,\
    ValidationError
from ..models import User
from flask_login import current_user



class RegisterForm(FlaskForm):
    email = StringField('', validators=[DataRequired(message="请输入邮箱地址"),
                                        Length(1, 64),
                                        Email(message="必须是合法的邮箱地址")])
    username = StringField('', validators=[DataRequired(message="请输入用户名"),
                                           Length(1, 20), Regexp(
                                        '^[A-Za-z][A-Za-z0-9_]*$', flags=0,
                                        message="用户名必须是数字、字母或下划线的组合")])
    password = PasswordField('', validators=[
        DataRequired(), EqualTo('password2', message='两次密码输入不一致')])
    password2 = PasswordField('', validators=[DataRequired()])


    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在，请重新输入或登录')

    def validate_username(form, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在，请重新输入')


class ChangeEmailForm(FlaskForm):
    email = StringField('请输入新的邮箱', validators=[DataRequired(message='请输入邮箱地址'),
                                        Length(1, 64),
                                        Email(message="必须是合法的邮箱地址"),
                                        EqualTo('email2', message='两次邮箱输入不一致')])
    email2 = StringField('请重复以上的邮箱', validators=[DataRequired(message='请输入邮箱地址'),
                                                Length(1, 64),
                                                Email(message="必须是合法的邮箱地址")])
    password = PasswordField('账户密码', validators=[DataRequired()])
    submit = SubmitField('更新邮箱')

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在，请重新输入或登录')

    def validate_password(form, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('用户密码错误')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('', validators=[DataRequired(message='请输入邮箱地址'),
                                            Length(1, 64),
                                            Email(message='必须是合法的邮箱地址')])

    def validate_email(form, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('用户邮箱不存在')


class ResetPasswordForm(FlaskForm):
    email = StringField('', validators=[DataRequired(message='请输入邮箱地址'),
                                        Length(1, 64),
                                        Email(message='必须是合法的邮箱地址')])
    password = PasswordField('', validators=[DataRequired(),
                                EqualTo('password2', message='两次密码输入不一致')])
    password2 = PasswordField('', validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('', validators=[
        DataRequired(message='请输入原始密码'), Length(1, 64)])
    password = PasswordField('', validators=[DataRequired(message='请输入密码'),
                                             Length(1, 64),
                                    EqualTo('password2', message='两次密码不一致')])
    password2 = PasswordField('', validators=[DataRequired(message='请输入密码'),
                                              Length(1, 64)])

    def validate_old_password(form, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('旧密码输入不正确')
