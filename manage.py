#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

from app import create_app, db
from app.models import User, Post
from flask_script import Manager, Shell, Server

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
manager.add_command('runserver', Server(host='127.0.0.1', port=5000))

def _make_context():
    return dict(app=app, db=db, User=User, Post=Post)

manager.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()