# -*- coding: utf-8 -*-

from datetime import datetime
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app, request
from markdown import markdown
import bleach
from itsdangerous import TimedJSONWebSignatureSerializer
from hashlib import md5


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    name = db.Column(db.String(80))
    incog_email = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    register_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    confirmed = db.Column(db.BOOLEAN, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    avatar_hash = db.Column(db.String(32))
    anonymous = db.Column(db.String(2))

    def __repr__(self):
        return 'User %r' % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, pswd):
        self.password_hash = generate_password_hash(pswd)

    def verify_password(self, pswd):
        return check_password_hash(self.password_hash, pswd)

    def generate_confirmation_token(self, expiration=2*60*60):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'],
                                            expires_in=expiration)
        return s.dumps({'confirm': self.id})

    # To validate the token
    def confirm(self, token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    # update last access
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    # generate change email token
    def generate_change_email_token(self, new_email, expiration=2*60*60):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'],
                                            expires_in=expiration)
        return s.dumps({'change_email': self.id,
                        'email_address': new_email})

    # change user email
    def confirm_change_email(self, token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        new_mail = data.get('email_address')
        if data.get('change_email') == self.id:
            self.email = new_mail
            self.avatar_hash = md5(new_mail.encode('utf-8')).hexdigest()
            db.session.add(self)
            db.session.commit()
            return True
        return False

    # reset password
    def generate_reset_password(self, expiration=2*60*60):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'],
                                            expires_in=expiration)
        return s.dumps({'reset_password': self.id})

    def confirm_reset_password(self, token, new_password):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_password') == self.id:
            self.password = new_password
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def change_password(self, new_password):
        if new_password:
            self.password = new_password
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def gravatar(self, size=45, default='retro', rating='x'):
        if request.is_secure:
            header = 'https://www.gravatar.com/avatar'
        else:
            header = 'http://www.gravatar.com/avatar'
        if self.avatar_hash:
            hash = self.avatar_hash
        elif self.email:
            hash = md5(self.email.encode('utf-8')).hexdigest()
        elif self.incog_email:
            hash = md5(self.incog_email.encode('utf-8')).hexdigest()
        return '{}/{}?s={}&d={}&r={}'.format(
            header, hash, size, default, rating
        )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # initialize avatar md5 hash
        if self.email and self.avatar_hash is None:
            self.avatar_hash = md5(self.email.encode('utf-8')).hexdigest()
            db.session.add(self)
            db.session.commit()
        elif self.incog_email and self.avatar_hash is None:
            self.avatar_hash = md5(self.incog_email.encode('utf-8')).hexdigest()
            db.session.add(self)
            db.session.commit()


# flask-login user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# helper table that is used for the relationship
tags_rel = db.Table('tags_rel',
                    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')))

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), index=True)

    def __repr__(self):
        return 'Tags %r' % self.name


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), index=True)
    brief_title = db.Column(db.String(240), index=True)
    subtitle = db.Column(db.String(240), index=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    picture = db.Column(db.String(80))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # modified timestamp
    mtimestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=tags_rel,
                           backref=db.backref('posts', lazy='dynamic'),
                           lazy='dynamic')

    def __repr__(self):
        return 'Post by %r' % self.author_id

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel', 'title'],
            'img': ['alt', 'src', 'height', 'width', 'align']
        }
        target.body_html = bleach.clean(markdown(value, output_format='html'),
                        tags=allowed_tags, attributes=attrs, strip=True)

    @staticmethod
    def if_modified_update_mtimestamp(target, value, oldvalue, initiator):
        if value != oldvalue:
            target.mtimestamp = datetime.utcnow()

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.body, 'set', Post.if_modified_update_mtimestamp)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    ctime = db.Column(db.DateTime, default=datetime.utcnow)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return 'Comment in post %r' % self.post_id

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'pre', 'strong']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel', 'title'],
        }
        target.body_html = bleach.clean(markdown(value, output_format='html'),
                        tags=allowed_tags, attributes=attrs, strip=True)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Book(db.Model):
    '''豆瓣图书'''
    __bind_key__ = 'collection'
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text)
    url = db.Column(db.Text)
    title = db.Column(db.Text)
    author = db.Column(db.String(20))


class Github(db.Model):
    ''' github trending '''
    __bind_key__ = 'collection'
    __tablename__ = 'trends'
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String(256))
    url = db.Column(db.Text)
    desc = db.Column(db.Text)
    language = db.Column(db.String(64))
    star = db.Column(db.String(64))


class SegmentFault(db.Model):
    ''' segmentfault 热门头条'''
    __bind_key__ = 'collection'
    __tablename__ = 'segment'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.Text)
    url = db.Column(db.Text)
    specs = db.Column(db.Text)
    collect = db.Column(db.Text)
    
