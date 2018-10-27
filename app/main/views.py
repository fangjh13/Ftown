# -*- coding: utf-8 -*-

from . import main
from .. import redis_store
from ..models import Post, Comment
from app import db
from flask import render_template, url_for, redirect
from flask_login import current_user
from ..blog.forms import CommentForm, CommentOpenForm
import os
from app.email import send_mail
import json
import datetime


def convert_time(timestamp):
    utc_8 = datetime.timezone(datetime.timedelta(hours=8))
    d = datetime.datetime.fromtimestamp(float(timestamp)
                    ).replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(utc_8)


@main.route('/')
def index():
    # 豆瓣图书
    # 虚构类
    books1 = redis_store.lrange('douban_book_fiction:data', 0, 2)
    # 非虚构类
    books2 = redis_store.lrange('douban_book_non_fiction:data', 0, 1)
    books = [json.loads(book) for book in (books1 + books2)]
    books_time = convert_time(
        redis_store.get('douban_book_fiction:timestamp').decode('utf-8')
    ).strftime('%m-%d %H:%M')

    # GitHub
    projects = [json.loads(i) for i in redis_store.lrange('github:data', 0, -1)]
    projects_time = convert_time(
        redis_store.get('github:timestamp').decode('utf-8')
    ).strftime('%m-%d %H:%M')

    # SegmentFault
    segments = [json.loads(i) for i in redis_store.lrange('segmentfault:data', 0, 14)]
    segments_time = convert_time(
        redis_store.get('segmentfault:timestamp').decode('utf-8')
    ).strftime('%m-%d %H:%M')

    # juejin
    juejins = [json.loads(i) for i in redis_store.lrange('juejin:data', 0, 14)]
    juejins_time = convert_time(
        redis_store.get('juejin:timestamp').decode('utf-8')
    ).strftime('%m-%d %H:%M')

    # hacker news
    h_news = [json.loads(i) for i in redis_store.lrange('hacker_news:data', 0, 19)]
    h_news_time = convert_time(
        redis_store.get('hacker_news:timestamp').decode('utf-8')
    ).strftime('%m-%d %H:%M')
    return render_template('book/index.html',
                           books=books, books_time=books_time,
                           projects=projects, projects_time=projects_time,
                           segments=segments, segments_time=segments_time,
                           juejins=juejins, juejins_time=juejins_time,
                           h_news=h_news, h_news_time=h_news_time)


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
