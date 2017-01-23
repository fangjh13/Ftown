# -*- coding: utf-8 -*-

from . import blog
from flask import render_template

@blog.route('/')
def home():
    return render_template('/blog/home.html')