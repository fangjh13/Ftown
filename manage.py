#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

# import local environment
if os.path.exists('.env'):
    print('Import environment from .env ...')
    with open('.env') as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value


from app import create_app, db
from app.models import User, Post, Comment, Tag
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FTOWN_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('runserver', Server(host='127.0.0.1', port=5000))

def _make_context():
    return dict(app=app, db=db, User=User, Post=Post, Comment=Comment,
                Tag=Tag)

manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()