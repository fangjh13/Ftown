# -*- coding: utf-8 -*-

import unittest
from app import db, create_app
from app.models import Comment, User, Post


class CommentCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        c = Comment(body='body')
        p = Post(title='title', body='body')
        db.session.add_all([c, p])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_comment_basic(self):
        c = Comment.query.first()
        self.assertTrue(c)
        self.assertTrue(c.ctime)
        self.assertTrue(c.body_html)

    def test_body_html_event(self):
        c = Comment.query.first()
        c.body = '`code`'
        db.session.add(c)
        db.session.commit()
        c = Comment.query.first()
        self.assertTrue(c.body_html == '<code>code</code>')

    def test_anonymous_partition(self):
        u = User(name='anonymous', incog_email='incognito@example.com',
                 anonymous=True)
        p = Post.query.first()
        c = Comment(body='<code>code</code>', author=u, post=p)
        db.session.add_all([u, c])
        n = User.query.first()
        self.assertTrue(n)
        total = Comment.query.all()
        self.assertTrue(len(total) == 2)
