# -*- coding: utf-8 -*-

from . import auth
from flask import redirect, render_template, request

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        d = request.form.get('email')
        print(d)
        return redirect('/')
    return render_template('/auth/login.html')