# -*- coding: utf-8 -*-

from . import main
from ..models import Book, Github, SegmentFault, JueJin, Post, Comment
from app import db
from flask import render_template, url_for, redirect
from flask_login import current_user
from ..blog.forms import CommentForm, CommentOpenForm
import os
from app.email import send_mail


@main.route('/')
def index():
    books = Book.query.all()
    projects = Github.query.limit(15).all()
    segments = SegmentFault.query.limit(15).all()
    juejins = JueJin.query.limit(15).all()
    return render_template('book/index.html', books=books, projects=projects,
                           segments=segments, juejins=juejins)


@main.route('/google000f78e215d2609a.html')
def google_verification():
    # Google site verification
    return render_template('google/google000f78e215d2609a.html')


@main.route('/resume', methods=['GET', 'POST'])
def my_resume():
    post = Post.query.filter_by(title='resume').first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        c = Comment(body=content, author=current_user, post=post)
        db.session.add(c)
        db.session.commit()
        # send remind email when comment
        subject = '简历有新的评论'
        addr = url_for('main.my_resume', _external=True)
        send_mail(subject,
                  "Blog Admin <{0}>".format(os.environ.get('MAIL_USERNAME')),
                  recipients=[post.author.email],
                  prefix_template='/mail/comment_remind',
                  addr=addr, content=content)
        return redirect(url_for('main.my_resume'))
    comments = post.comments.all()
    count = post.comments.count()
    post.views += 1
    db.session.add(post)
    db.session.commit()
    open_form = CommentOpenForm()
    return render_template('blog/post.html', post=post, form=form,
                           comments=comments, count=count, open_form=open_form)
