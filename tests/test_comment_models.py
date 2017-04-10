# -*- coding: utf-8 -*-

import unittest
from app import db, create_app
from app.models import Comment

class CommentCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        c = Comment(body='body')
        db.session.add(c)
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
        c.body = 'new body'
        db.session.add(c)
        db.session.commit()
        c = Comment.query.first()
        self.assertTrue(c.body_html == '<p>new body</p>')