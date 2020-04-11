# -*- coding: utf-8 -*-

import unittest
from app import db, create_app
from app.models import Post
import time

class PostCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        p = Post(title='title', body='body')
        db.session.add(p)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_post_basic(self):
        p = Post.query.first()
        self.assertTrue(p)
        self.assertTrue(p.timestamp)
        self.assertTrue(p.body)
        self.assertTrue(p.body_html)

    def test_on_change(self):
        p = Post.query.first()
        old_time = p.mtimestamp
        time.sleep(1)
        p.body = 'modified'
        db.session.add(p)
        db.session.commit()
        p = Post.query.first()
        self.assertTrue(p.body_html == '<p>modified</p>')
        self.assertTrue(p.mtimestamp != old_time)
