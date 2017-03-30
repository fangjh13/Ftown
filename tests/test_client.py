# -*- coding: utf-8 -*-


import unittest
from app import create_app, db, mail
from app.models import User, Post
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
        u = User(email='test@example.com', password='123456', confirmed=True)
        db.session.add(u)
        db.session.commit()
        p = Post(title='test_post', body='post body', author=u)
        db.session.add(p)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_main_index(self):
        response = self.client.get(url_for('main.index'),
                                   follow_redirects=True)
        self.assertTrue(b'Fython' in response.data)

    def test_blog_index(self):
        response = self.client.get(url_for('blog.home'))
        self.assertTrue(b'Hello Blog' in response.data)

    def test_blog_about(self):
        response = self.client.get(url_for('blog.about'))
        self.assertTrue(b'About Me' in response.data)

    def test_user_login_logout(self):
        # login
        response = self.client.post(url_for('auth.login'), data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
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
        self.assertTrue('忘记密码?'.encode('utf-8') in response.data)

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

    def test_post_views(self):
        p = Post.query.first()
        self.assertTrue(p.views==0)
        self.client.get(url_for('blog.post'))
        p = Post.query.first()
        response = self.client.get('/blog/post/1')
        self.assertTrue("浏览量 2".encode('utf-8') in response.data)
        p = Post.query.first()
        self.assertTrue(p.views==2)

    def test_index_like(self):
        p = Post.query.first()
        self.assertTrue(p.likes==0)
        response = self.client.get(url_for('blog.like', id=p.id),
                                   follow_redirects=True)
        self.assertTrue(b'1 Likes' in response.data)
        p1 = Post.query.first()
        self.assertTrue(p1.likes==1)

    def test_user_register_index(self):
        response = self.client.get(url_for('auth.register'))
        self.assertTrue('注册'.encode('utf-8') in response.data)

    def test_user_register_invalid_password(self):
        response = self.client.post(url_for('auth.register'),
                        data=dict(email='test2@example.com',
                                  username='user',
                                  password='1234',
                                  password2='12345'),
                        follow_redirects=True)
        self.assertTrue('两次密码输入不一致'.encode('utf-8') in response.data)

    def test_user_register_unconfirmed(self):
        response = self.client.post(url_for('auth.register'),
                                    data=dict(email='test2@example.com',
                                              username='user',
                                              password='12345',
                                              password2='12345'),
                                    follow_redirects=True)
        self.assertTrue('用户验证邮箱已发送到您的邮箱，请查收'.encode('utf-8') in response.data)
        response = self.client.post(url_for('auth.login'),
                                    data=dict(email='test2@example.com',
                                              password='12345'),
                                    follow_redirects=True)
        self.assertTrue('你的邮箱账户未激活'.encode('utf-8') in response.data)

    def test_change_email(self):
        # login user
        self.client.post(url_for('auth.login'), data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
        response = self.client.post(url_for('auth.change_email_request'),
                                    data=dict(email='change2email@example.com',
                                              email2='change2email@example.com',
                                              password='wrong password'),
                                    follow_redirects=True)
        self.assertTrue('用户密码错误'.encode('utf-8') in response.data)
        response = self.client.post(url_for('auth.change_email_request'),
                                    data=dict(email='change2email@example.com',
                                              email2='change2email@example.com',
                                              password='123456'),
                                    follow_redirects=True)
        self.assertTrue('更换邮箱的邮件已重新发送到您新的邮箱'.encode('utf-8') in response.data)

    def test_reset_password_request(self):
        response = self.client.get(url_for('auth.reset_password_request'))
        self.assertTrue('重置密码'.encode('utf-8') in response.data)
        response = self.client.post(url_for('auth.reset_password_request'),
                                    data=dict(email='not_exist@example.com'),
                                    follow_redirects=True)
        self.assertTrue('用户邮箱不存在'.encode('utf-8') in response.data)


    def test_reset_password(self):
        response = self.client.get(url_for('auth.reset_password', token='errorToken'))
        self.assertTrue('重置密码'.encode('utf-8') in response.data)
        response = self.client.post(url_for('auth.reset_password', token='errorToken'),
                                    data=dict(email='test@example.com',
                                              password='123456',
                                              password2='123'),
                                    follow_redirects=True)
        self.assertTrue('两次密码输入不一致'.encode('utf-8') in response.data)
        response = self.client.post(url_for('auth.reset_password', token='errorToken'),
                                    data=dict(email='test@example.com',
                                              password='1',
                                              password2='1'),
                                    follow_redirects=True)
        self.assertTrue('链接非法或已过期'.encode('utf-8') in response.data)

