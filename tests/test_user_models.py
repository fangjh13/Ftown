# -*- coding: utf-8 -*-


import unittest
from app.models import User, Post
from app import create_app, db


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_alive(self):
        u = User(username='test', email='test@example.com', password='1234')
        db.session.add(u)
        db.session.commit()
        r = User.query.filter_by(username='test').first()
        self.assertTrue(r)

    def test_password_setter(self):
        u = User(password='1234')
        self.assertTrue(u.password_hash is not None)

    def test_password_getter(self):
        u = User(password='1234')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verify(self):
        u = User(username='test', email='test@example.com', password='1234')
        db.session.add(u)
        db.session.commit()
        r = User.query.filter_by(username='test').first()
        self.assertTrue(r.verify_password('1234'))
        self.assertFalse(r.verify_password('111'))

    def test_user_post(self):
        u = User()
        p = Post(id=3, author=u)
        db.session.add_all([u, p])
        db.session.commit()
        p1 = Post.query.get(3)
        self.assertTrue(p1.author == u)

