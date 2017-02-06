# -*- coding: utf-8 -*-

from . import blog
from flask import render_template

@blog.route('/')
def home():
    return render_template('/blog/home.html')


@blog.route('/about')
def about():
    return render_template('/blog/about.html')


@blog.route('/post')
def post():
    return render_template('/blog/post.html')


@blog.route('/contact')
def contact():
    return render_template('/blog/contact.html')