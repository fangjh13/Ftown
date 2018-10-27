#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from dotenv import load_dotenv

# import local environment
if os.path.exists('.env'):
    print('Import environment from .env ...')
    load_dotenv(verbose=True)

from app import create_app, db
from app.models import User, Post, Comment, Tag
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FTOWN_CONFIG') or 'default')

migrate = Migrate(app, db)


@app.shell_context_processor
def _make_context():
    return dict(app=app, db=db, User=User, Post=Post, Comment=Comment,
                Tag=Tag)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


