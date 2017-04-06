# -*- coding: utf-8 -*-


import unittest
from app.models import User, Post
from app import create_app, db
import time


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

    def test_user_validate_confirmed(self):
        u = User()
        db.session.add(u)
        db.session.commit()
        u1 = User.query.first()
        self.assertTrue(u1.confirmed==False)
        token = u1.generate_confirmation_token()
        self.assertTrue(u1.confirm(token))
        u2 = User.query.first()
        self.assertTrue(u2.confirmed)

    def test_user_invalidate_confirmed(self):
        u = User()
        db.session.add(u)
        db.session.commit()
        u1 = User.query.first()
        token = u1.generate_confirmation_token(5)
        time.sleep(6)
        self.assertFalse(u1.confirm(token))
        u2 = User.query.first()
        self.assertFalse(u2.confirmed == True)

    def test_user_last_seen(self):
        u = User()
        db.session.add(u)
        db.session.commit()
        u1 = User.query.first()
        first = u1.last_seen
        time.sleep(2)
        u1.ping()
        u2 = User.query.first()
        self.assertTrue(u2.last_seen != first)

    def test_change_mail(self):
        u = User(email='test@example.com')
        db.session.add(u)
        db.session.commit()
        u = User.query.first()
        token = u.generate_change_email_token('new_emial@example.com', 2)
        self.assertTrue(token is not None)
        self.assertTrue(u.confirm_change_email(token))
        # token timeout
        time.sleep(3)
        self.assertFalse(u.confirm_change_email(token))

    def test_generate_reset_password(self):
        u = User(email='test@example.com', password='123456')
        db.session.add(u)
        db.session.commit()
        u = User.query.first()
        token = u.generate_reset_password(2)
        self.assertTrue(token is not None)
        self.assertTrue(u.confirm_reset_password(token, 'abc'))
        time.sleep(3)
        self.assertFalse(u.confirm_reset_password(token, 'def'))
        u1 = User.query.first()
        self.assertTrue(u1.verify_password('abc'))

    def test_change_user_password(self):
        u = User(email='test@example.com', password='123456')
        db.session.add(u)
        db.session.commit()
        u = User.query.first()
        u.change_password('123')
        u = User.query.first()
        self.assertFalse(u.verify_password('123456'))
        self.assertTrue(u.verify_password('123'))
