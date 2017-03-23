# -*- coding: utf-8 -*-

from . import auth
from flask import redirect, render_template, request, url_for, flash
from ..models import User
from flask_login import login_user, logout_user
from urllib.parse import urlparse, urljoin
from .forms import RegisterForm
from app import db
from flask_login import current_user, login_required
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
    elif not current_user.confirmed:
        current_user.confirm(token)
        return redirect(url_for('blog.home'))
    else:
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