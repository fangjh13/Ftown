# -*- coding: utf-8 -*-

from . import auth
from flask import redirect, render_template, request, url_for, flash
from ..models import User
from flask_login import login_user, logout_user, current_user, \
    login_required
from urllib.parse import urlparse, urljoin
from .forms import RegisterForm, ChangeEmailForm, ResetPasswordForm, \
    ResetPasswordRequestForm, ChangePasswordForm
from app import db
from ..email import send_mail
import os


# A function that ensures that a redirect target will lead to the same server
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
            ref_url.netloc == test_url.netloc


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            user = User.query.filter_by(email=email).first()
            if user and user.verify_password(password):
               login_user(user, request.form.get('remember_me'))
               next = request.values.get('next')
               if not is_safe_url(next):
                   next = None
               return redirect(next or url_for('blog.home'))
            flash('用户名或密码错误，请重试。')
    return render_template('/auth/login.html')


@auth.route('/logout')
def logout():
    logout_user()
    flash('你已经退出登录')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        send_mail(subject="[书床]邮箱激活",
                  sender="书床管理员 <{}>".format(os.getenv('MAIL_USERNAME')),
                  recipients=[user.email],
                  prefix_template="/auth/mail/confirm",
                  user=user,
                  token=user.generate_confirmation_token(expiration=2*60*60))
        flash('用户验证邮箱已发送到您的邮箱，请查收')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('blog.home'))
    else:
        if current_user.confirm(token):
            return redirect(url_for('blog.home'))
        flash('链接已过期或用户错误，请重新登入')
        return redirect(url_for('auth.login'))


# resent confirm email
@auth.route('/confirm')
@login_required
def resend_confirm():
    token = current_user.generate_confirmation_token(expiration=2*60*60)
    send_mail(subject="[书床]邮箱激活",
              sender="书床管理员 <{}>".format(os.getenv('MAIL_USERNAME')),
              recipients=[current_user.email],
              prefix_template="/auth/mail/confirm",
              user=current_user,
              token=token)
    flash('用户验证邮箱已重新发送到您的邮箱，请查收')
    return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('blog.home'))
    return render_template('auth/unconfirmed.html')


@auth.route('/change-email', methods=['POST', 'GET'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.email.data
        token = current_user.generate_change_email_token(new_email)
        send_mail(subject="[书床]更换新邮箱",
                  sender="书床管理员 <{}>".format(os.getenv('MAIL_USERNAME')),
                  recipients=[new_email],
                  prefix_template="/auth/mail/change_email",
                  user=current_user,
                  token=token)
        flash('更换邮箱的邮件已重新发送到您新的邮箱，请查收')
        return redirect(url_for('auth.login'))
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.confirm_change_email(token):
        flash('邮箱已经更改，请点击以下链接重新发送验证邮件完成验证')
    else:
        flash('更新邮箱验证失败，请重试')
    return redirect(url_for('main.index'))


@auth.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first_or_404()
        token = user.generate_reset_password()
        send_mail(subject="[书床]重置密码",
                  sender="书床管理员 <{}>".format(os.getenv('MAIL_USERNAME')),
                  recipients=[email],
                  prefix_template="/auth/mail/reset",
                  user=user,
                  token=token)
        flash('重置密码的邮件已发送你的邮箱，请尽快去修改')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first_or_404()
        if user.confirm_reset_password(token, password):
            flash('用户密码已更新，请重新登录')
        else:
            flash('链接非法或已过期')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = current_user
    form = ChangePasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        if user.change_password(password):
            flash('密码已更新，请重新登录')
            logout_user()
        else:
            flash('密码更新失败')
        return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)
