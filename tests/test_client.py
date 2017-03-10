# -*- coding: utf-8 -*-


import unittest
from app import create_app, db, mail
from app.models import User
from flask import url_for
import os


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
        response = self.client.get(url_for('blog.dashboard'),
                                   follow_redirects=True)
        self.assertTrue(response.status_code==200)
        self.assertTrue(b'Forgot Password?' in response.data)

    def test_user_login_with_invalid(self):
        # login with invaild password
        response = self.client.post(url_for('auth.login'), data=dict(
            email='test@example.com', password='123'), follow_redirects=True)
        # test flash message
        self.assertTrue('用户名或密码错误，请重试'.encode('utf-8') in response.data)

    def test_contact_send_email(self):
        ## can receive a letter must set `MAIL_SUPPRESS_SEND = False`

        #response = self.client.post(url_for('blog.contact'), data=dict(
        #    name='unittest', email='unittest@example.com',
        #    message='unittest message'))
        #self.assertTrue('提交成功，我会很快联系你的'.encode('utf-8') in response.data)
        # keep track of dispatched emails
        with mail.record_messages() as outbox:
            mail.send_message(subject='unittest', body='test',
                sender="Blog Unittest <{0}>".format(os.environ.get('MAIL_USERNAME')),
                recipients=['616960344@qq.com'])
            self.assertTrue(len(outbox) == 1)
            self.assertTrue(outbox[0].subject == 'unittest')
