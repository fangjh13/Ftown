# -*- coding: utf-8 -*-

from datetime import datetime
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask import current_app
from markdown import markdown
import bleach
from itsdangerous import TimedJSONWebSignatureSerializer


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True)
    register_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    confirmed = db.Column(db.BOOLEAN, default=False)

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
        if data['confirm'] != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

# flask-login user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), index=True)
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
            'img': ['alt', 'src']
        }
        target.body_html = bleach.clean(markdown(value, output_format='html'),
                        tags=allowed_tags, attributes=attrs, strip=True)

db.event.listen(Post.body, 'set', Post.on_changed_body)


# class Comment(db.Model):
#     __tablename__ = 'comments'
#     id = db.Column(db.Integer, primary_key=True)

