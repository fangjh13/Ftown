# -*- coding: utf-8 -*-

import os
from datetime import datetime

from flask import render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

from app import db
from . import blog
from .forms import WriteForm
from ..email import send_mail
from ..models import User, Post


# Blog background management authentication
# from flask_httpauth import HTTPBasicAuth
# auth = HTTPBasicAuth()
#
# @auth.verify_password
# def verify_pswd(username, password):
#     # blog administrator is `BlogAdmin`
#     if username == 'BlogAdmin':
#         blogadmin = User.query.filter_by(username='BlogAdmin').first_or_404()
#         if blogadmin.verify_password(password):
#             return True
#     return False



@blog.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    fython = User.query.filter_by(username='Fython').first_or_404()
    # flask-SQLAlchemy Pagination
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
def dashboard():
    fython = User.query.filter_by(username='Fython').first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = fython.posts.order_by(Post.timestamp.desc()).paginate(
        page, 10, error_out=False)
    posts = pagination.items
    return render_template('/blog/dashboard.html', posts=posts, pagination=pagination,
                                                                endpoint='blog.dashboard')


@blog.route('/write', methods=['GET', 'POST'])
def write():
    form = WriteForm()
    if form.validate_on_submit():
        # save uploaded picture
        p = form.picture.data
        filename = secure_filename(p.filename)
          # unique filename
        split = os.path.splitext(filename)
        id = Post.query.order_by(Post.id.desc()).first().id + 1
        filename = split[0] + '-' + str(id) + split[1]
        dirpath = os.path.abspath(os.path.dirname(__name__))
        p.save(os.path.join(dirpath, 'app/static/img', filename))

        title = form.title.data
        subtitle = form.subtitle.data
        body = form.body.data

        u = User.query.filter_by(username='Fython').first_or_404()
        p = Post(picture=filename, title=title, subtitle=subtitle,
                 body=body, author=u)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('blog.post'))
    return render_template('/blog/write.html', form=form)


@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    p = Post.query.filter_by(id=id).first_or_404()
    form = WriteForm()
    if form.validate_on_submit():
        pic = form.picture.data
        filename = secure_filename(pic.name)
        split = os.path.splitext(filename)
        suffix = p.id
        filename = split[0] + '-' + str(suffix) + split[1]
        dirpath = os.path.abspath(os.path.dirname(__name__))
        pic.save(os.path.join(dirpath, 'app/static/img', filename))

        p.picture = filename
        p.title = form.title.data
        p.subtitle = form.subtitle.data
        p.body = form.body.data
        p.mtimestamp = datetime.utcnow()
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('blog.onepost', post_id=id))
    form.title.data = p.title
    form.subtitle.data = p.subtitle
    form.body.data = p.body
    return render_template('/blog/write.html', form=form)


@blog.route('/delete/<int:id>')
def delete(id):
    p = Post.query.filter_by(id=id).first_or_404()
    db.session.delete(p)
    db.session.commit()
    flash('DELETE SUCCESS')
    return redirect(url_for('blog.dashboard'))
