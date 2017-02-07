# -*- coding: utf-8 -*-

from . import blog
from flask import render_template
from ..models import User

@blog.route('/')
def home():
    fython = User.query.filter_by(username='Fython').first_or_404()
    posts = fython.posts.all()
    return render_template('/blog/home.html', posts=posts)


@blog.route('/about')
def about():
    return render_template('/blog/about.html')


@blog.route('/post')
def post():
    return render_template('/blog/post.html')


@blog.route('/contact')
def contact():
    return render_template('/blog/contact.html')