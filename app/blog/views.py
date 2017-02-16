# -*- coding: utf-8 -*-

from . import blog
import os
from flask import render_template, request, flash, redirect, url_for
from ..models import User, Post
from ..email import send_mail
from flask_httpauth import HTTPBasicAuth


# Blog background management authentication
auth = HTTPBasicAuth()

@auth.verify_password
def verify_pswd(username, password):
    # blog administrator is `BlogAdmin`
    if username == 'BlogAdmin':
        blogadmin = User.query.filter_by(username='BlogAdmin').first_or_404()
        if blogadmin.verify_password(password):
            return True
    return False



@blog.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    fython = User.query.filter_by(username='Fython').first_or_404()
    pagination = fython.posts.order_by(Post.timestamp.desc()).paginate(
        page, 4, error_out=False)
    posts = pagination.items
    return render_template('/blog/home.html', posts=posts, pagination=pagination)


@blog.route('/about')
def about():
    return render_template('/blog/about.html')


@blog.route('/post')
def post():
    post = Post.query.order_by(Post.timestamp.desc()).first_or_404()
    return render_template('/blog/post.html', post=post)

@blog.route('/post/<int:post_id>')
def onepost(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('/blog/post.html', post=post)


@blog.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        form = request.form
        subject = '[IMPORTANT REPLY] someone contact to you'
        send_mail(subject, "Blog Admin <{0}>".format(os.environ.get('MAIL_USERNAME')),
                  recipients=['616960344@qq.com'], template='/mail/mail_contact', form=form)
        flash('提交成功，我会很快联系你的')
        redirect(url_for('.contact'))
    return render_template('/blog/contact.html')


@blog.route('/dashboard')
@auth.login_required
def post_new_blog():
    return render_template('/blog/dashboard.html')

