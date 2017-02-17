# -*- coding: utf-8 -*-

from . import auth
from flask import redirect, render_template, request, url_for
from ..models import User
from flask_login import login_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            user = User.query.filter_by(email=email).first()
            if user and user.verify_password(password):
               login_user(user, request.form.get('remember_me'))
               next = request.args.get('next')
               return redirect(next or url_for('blog.home'))
    return render_template('/auth/login.html')
