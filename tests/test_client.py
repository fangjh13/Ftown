# -*- coding: utf-8 -*-


import unittest
from app import create_app, db
from app.models import User, Post, Comment, Tag
from flask import url_for
import time
import datetime


class FlaskClientCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        # insert a user
        u = User(email='test@example.com', username='test',
                 password='123456', confirmed=True)
        db.session.add(u)
        db.session.commit()
        # init tag
        t = Tag(name='TEST')
        t2 = Tag(name='INIT_TAG')
        p = Post(title='test_post', body='post body', author=u,
                 brief_title='brief_title_name')
        p.tags.append(t)
        db.session.add(p)
        db.session.commit()
        c = Comment(body='comment body', author=u, post=p)
        db.session.add(c)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # def test_main_index(self):
    #     response = self.client.get('/',
    #                                follow_redirects=True)
    #     self.assertTrue('博客' in response.get_data(as_text=True))

    def test_blog_index(self):
        response = self.client.get('/blog', follow_redirects=True)
        self.assertTrue('Hello Blog' in response.get_data(as_text=True))

    def test_blog_about(self):
        response = self.client.get('/blog/about')
        self.assertTrue(b'About Me' in response.data)

    def test_user_login_logout(self):
        # login
        response = self.client.post('/auth/login', data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
        self.assertTrue(b'Hello Blog' in response.data)
        # 'blog.dashboard' required login
        response = self.client.get('/blog/dashboard')
        self.assertTrue(response.status_code == 200)
        # logout
        self.client.get('/auth/logout')
        # try go to dashboard
        response = self.client.get('/blog/dashboard',
                                   follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue('忘记密码?'.encode('utf-8') in response.data)

    def test_user_login_with_invalid(self):
        # login with invaild password
        response = self.client.post('/auth/login', data=dict(
            email='test@example.com', password='123'), follow_redirects=True)
        # test flash message
        self.assertTrue('用户名或密码错误，请重试'.encode('utf-8') in response.data)

    # def test_contact_send_email(self):
    #     ## can receive a letter must set `MAIL_SUPPRESS_SEND = False`
    #
    #     response = self.client.post(url_for('blog.contact'), data=dict(
    #         name='unittest', email='unittest@example.com',
    #         message='unittest message'))
    #     self.assertTrue('提交成功，我会很快联系你的'.encode('utf-8') in response.data)
    #     # # keep track of dispatched emails
    #     # with mail.record_messages() as outbox:
    #     #     mail.send_message(subject='unittest', body='test',
    #     #         sender="Blog Unittest <{0}>".format(os.environ.get('MAIL_USERNAME')),
    #     #         recipients=['616960344@qq.com'])
    #     #     self.assertTrue(len(outbox) == 1)
    #     #     self.assertTrue(outbox[0].subject == 'unittest')

    def test_post_views(self):
        p = Post.query.first()
        self.assertTrue(p.views == 0)
        self.client.get('/blog/post')
        p = Post.query.first()
        response = self.client.get('/blog/post/1')
        self.assertTrue("浏览量 2".encode('utf-8') in response.data)
        self.assertTrue(b'comment body' in response.data)
        p = Post.query.first()
        self.assertTrue(p.views == 2)

    def test_index_like(self):
        p = Post.query.first()
        self.assertTrue(p.likes == 0)
        response = self.client.get('/blog/like/{}'.format(p.id),
                                   follow_redirects=True)
        self.assertTrue(b'1 Likes' in response.data)
        p1 = Post.query.first()
        self.assertTrue(p1.likes == 1)

    def test_user_register_index(self):
        response = self.client.get('/auth/register')
        self.assertTrue('注册'.encode('utf-8') in response.data)

    def test_user_register_invalid_password(self):
        response = self.client.post('/auth/register',
                                    data=dict(email='test2@example.com',
                                              username='user',
                                              password='1234',
                                              password2='12345'),
                                    follow_redirects=True)
        self.assertTrue('两次密码输入不一致'.encode('utf-8') in response.data)

    def test_user_register_unconfirmed(self):
        response = self.client.post('/auth/register',
                                    data=dict(email='test2@example.com',
                                              username='user',
                                              password='12345',
                                              password2='12345'),
                                    follow_redirects=True)
        self.assertTrue('用户验证邮箱已发送到您的邮箱，请查收'.encode('utf-8')
                        in response.data)
        response = self.client.post('/auth/login',
                                    data=dict(email='test2@example.com',
                                              password='12345'),
                                    follow_redirects=True)
        self.assertTrue('你的邮箱账户未激活'.encode('utf-8') in response.data)

    def test_change_email(self):
        # login user
        self.client.post('/auth/login', data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
        response = self.client.post('/auth/change-email',
                                    data=dict(email='change2email@example.com',
                                              email2='change2email@example.com',
                                              password='wrong password'),
                                    follow_redirects=True)
        self.assertTrue('用户密码错误' in response.get_data(as_text=True))
        response = self.client.post('/auth/change-email',
                                    data=dict(email='change2email@example.com',
                                              email2='change2email@example.com',
                                              password='123456'),
                                    follow_redirects=True)
        self.assertTrue('更换邮箱的邮件已重新发送到您新的邮箱'.encode('utf-8')
                        in response.data)

    def test_reset_password_request(self):
        response = self.client.get('/auth/reset', follow_redirects=True)
        self.assertTrue('重置密码' in response.get_data(as_text=True))
        response = self.client.post('/auth/reset',
                                    data=dict(email='not_exist@example.com'),
                                    follow_redirects=True)
        self.assertTrue('用户邮箱不存在' in response.get_data(as_text=True))

    def test_reset_password(self):
        response = self.client.get('/auth/reset/{}'.format('errorToken'))
        self.assertTrue('重置密码' in response.get_data(as_text=True))
        response = self.client.post('/auth/reset/{}'.format('errorToken'),
                                    data=dict(email='test@example.com',
                                              password='123456',
                                              password2='123'),
                                    follow_redirects=True)
        self.assertTrue('两次密码输入不一致' in response.get_data(as_text=True))
        response = self.client.post('/auth/reset/{}'.format('errorToken'),
                                    data=dict(email='test@example.com',
                                              password='1',
                                              password2='1'),
                                    follow_redirects=True)
        self.assertTrue('链接非法或已过期' in response.get_data(as_text=True))

    def test_change_password(self):
        response = self.client.get('/auth/change-password',
                                   follow_redirects=True)
        self.assertTrue('用户未登录，请先登录' in response.get_data(as_text=True))
        response = self.client.post('/auth/login', data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
        response = self.client.post('/auth/change-password',
                                    data=dict(old_password='123',
                                              password='111',
                                              password2='111'),
                                    follow_redirects=True)
        self.assertTrue('旧密码输入不正确'.encode('utf-8') in response.data)

    def test_single_user_posts(self):
        response = self.client.get('/post/test', follow_redirects=True)
        self.assertTrue(b'test_post' in response.data)

    def test_single_post(self):
        response = self.client.get('/blog/post/1', follow_redirects=True)
        self.assertTrue(b'comment body' in response.data)

    def test_post_comment(self):
        response = self.client.get('/blog/post')
        self.assertTrue('您还没有登录'.encode('utf-8') in
                        response.data)
        response = self.client.post('/auth/login', data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
        self.assertFalse('您还没有登录'.encode('utf-8') in
                         response.data)
        response = self.client.post('/blog/post', data=dict(
            content='test comment content'), follow_redirects=True)
        self.assertTrue(b'test comment content' in response.data)

    def test_tags(self):
        response = self.client.get('/blog', follow_redirects=True)
        self.assertTrue(b'TEST' in response.data)
        response = self.client.get('/blog/onepost/1', follow_redirects=True)
        self.assertTrue(b'TEST' in response.data)

    def test_sort_tags(self):
        response = self.client.get('/blog/tags/TEST'.format('TEST'))
        self.assertTrue(b'test_post' in response.data)

    def test_compose_post_with_tag(self):
        # login
        response = self.client.post('/auth/login', data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
        # post
        time.sleep(1)
        response = self.client.post('/blog/write', data=dict(
            title='test tag title', tags='test_tag;TWO', body='body'),
                                    follow_redirects=True)
        self.assertTrue('test_tag'.encode('utf-8') in response.data)

    def test_edit_post_with_tag(self):
        # login
        response = self.client.post('/auth/login', data=dict(
            email='test@example.com', password='123456'), follow_redirects=True)
        # edit post id=1
        response = self.client.post('/blog/edit/1', data=dict(
            title='title', tags='new_tag', body='body',
            brief_title='brief_title', id=1),
                                    follow_redirects=True)
        self.assertTrue(b'new_tag' in response.data)
        self.assertFalse(b'INIT_TAG' in response.data)

    def test_post_anonymous_comment(self):
        response = self.client.get('/blog/post')
        self.assertTrue('免登录入口' in response.get_data(as_text=True))
        response = self.client.post('/blog/post', data=dict(
            open_content='test', open_name='test_username',
            open_email='test@example.com'), follow_redirects=True)
        self.assertTrue(b'test_username' in response.data)
        today = datetime.date.today()
        y, m, d = today.year, today.month, today.day
        response = self.client.post('/blog/{}/{}/{}/{}'.format(
            y, m, d, 'brief_title_name'),
                                    data=dict(
                                        open_content='test',
                                        open_name='test_username_brief',
                                        open_email='test@example.com',
                                        open_captcha="abcd"),
                                    follow_redirects=True)
        self.assertTrue(b'test_username_brief' in response.data)

    def test_date_time_brief_title_url(self):
        today = datetime.datetime.now(datetime.timezone.utc)
        y, m, d = today.year, today.month, today.day
        response = self.client.get('/blog/{}/{}/{}/{}'.format(
            y, m, d, 'brief_title_name'), follow_redirects=True)
        self.assertTrue('test_post' in response.get_data(as_text=True))
        self.assertTrue('comment body' in response.get_data(as_text=True))
