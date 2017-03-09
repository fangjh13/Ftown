# -*- coding: utf-8 -*-


import unittest
from app import create_app, db
from app.models import User
from flask import url_for


class FlaskClientCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        # insert a user
        u = User(email='test@example.com', password='1234')
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_main_index(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue(b'Hello world' in response.data)

    def test_blog_index(self):
        response = self.client.get(url_for('blog.home'))
        self.assertTrue(b'Hello Blog' in response.data)

    def test_blog_about(self):
        response = self.client.get(url_for('blog.about'))
        self.assertTrue(b'About Me' in response.data)

    def test_user_login_logout(self):
        # login
        response = self.client.post(url_for('auth.login'), data=dict(
            email='test@example.com', password='1234'), follow_redirects=True)
        self.assertTrue(b'Hello Blog' in response.data)
        # 'blog.dashboard' required login
        response = self.client.get(url_for('blog.dashboard'))
        self.assertTrue(response.status_code==200)
        # logout
        self.client.get(url_for('auth.logout'))
        # try go to dashboard
        response = self.client.get(url_for('blog.dashboard'), follow_redirects=True)
        self.assertTrue(response.status_code==200)
        self.assertTrue(b'Forgot Password?' in response.data)

    def test_user_login_with_invalid(self):
        # login with invaild password
        response = self.client.post(url_for('auth.login'), data=dict(
            email='test@example.com', password='123'), follow_redirects=True)
        # test flash message
        print(response.data)
        self.assertTrue('用户名或密码错误，请重试'.encode('utf-8') in response.data)
