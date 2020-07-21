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
import click
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FTOWN_CONFIG') or 'default')

migrate = Migrate(app, db)


@app.shell_context_processor
def _make_context():
    return dict(app=app, db=db, User=User, Post=Post, Comment=Comment,
                Tag=Tag)


@app.cli.command()
@click.option('--pattern', default=None, help='test files that match pattern will be loaded.')
def test(pattern):
    """ project unit test """
    import unittest
    if pattern:
        tests = unittest.TestLoader().discover('tests', pattern)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command("search-reindex")
def search_reindex():
    """ reindex Posts searching use elasticsearch"""
    Post.reindex()


@app.cli.command("deploy")
def deploy():
    """ deloply project"""
    db.create_all()

