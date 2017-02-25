# -*- coding: utf-8 -*-

from . import auth
from flask import redirect, render_template, request, url_for, make_response
from ..models import User
from flask_login import login_user
from urllib.parse import urlparse, urljoin


# A function that ensures that a redirect target will lead to the same server
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
            ref_url.netloc == test_url.netloc


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
    return render_template('/auth/login.html')
