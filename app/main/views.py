# -*- coding: utf-8 -*-

from . import main
from flask import request
from flask_login import login_required, current_user


@main.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        print(request.host_url)
        print(current_user.username)
    return 'Hello world required login'