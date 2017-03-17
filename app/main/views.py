# -*- coding: utf-8 -*-

from . import main
from flask import redirect, url_for


@main.route('/')
def index():
   return redirect(url_for('blog.home'))