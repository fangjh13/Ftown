# -*- coding: utf-8 -*-

from datetime import datetime
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer
from hashlib import md5
import markdown
from typing import TypeVar, Tuple
from app.search import add_to_index, remove_from_index, query_index

# markdwon render
md = markdown.Markdown(extensions=['extra', 'codehilite', 'sane_lists', 'toc'])


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

    def generate_confirmation_token(self, expiration=2 * 60 * 60):
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
    def generate_change_email_token(self, new_email, expiration=2 * 60 * 60):
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
    def generate_reset_password(self, expiration=2 * 60 * 60):
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
        header = 'https://www.gravatar.com/avatar'
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

    def generate_basic_auth_token(self, expiration):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'],
                                            expires_in=expiration)
        return s.dumps({
            "basic_auth": self.id
        }).decode('utf-8')

    @staticmethod
    def verify_basic_auth_token(token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data.get('basic_auth', ''))


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


class SearchableMixin:
    @classmethod
    def search(cls, expression: str, page: int, per_page: int) -> Tuple[TypeVar('T'), int]:
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session) -> None:
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session) -> None:
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls) -> None:
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class Post(db.Model, SearchableMixin):
    __tablename__ = 'posts'
    __searchable__ = ['body_html', 'title', 'brief_title', 'subtitle']
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
        return f'Post by {self.author_id!r} post id {self.id!r}'

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = md.convert(value)

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
        target.body_html = md.convert(value)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)
