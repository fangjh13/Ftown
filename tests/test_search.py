import unittest
from app import create_app, db
from app.models import Post
from flask import current_app
import time
from app.search import add_to_index, remove_from_index, query_index


class ElasticSearchTestCast(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_es_exists(self):
        self.assertTrue(self.app.elasticsearch.ping())

    def test_es_add(self):
        p = Post(title='abc')
        db.session.add(p)
        db.session.commit()
        # sleep for handing
        time.sleep(1)
        self.assertEqual(1, query_index('posts', 'abc', 1, 10)[1])
        self.assertEqual(1, Post.search('abc', 1, 10)[1])
        current_app.elasticsearch.indices.delete('posts')

    def test_es_delete(self):
        p = Post(title='abc')
        db.session.add(p)
        db.session.commit()
        db.session.delete(p)
        db.session.commit()
        time.sleep(1)
        self.assertEqual(0, Post.search('abc', 1, 10)[1])
        current_app.elasticsearch.indices.delete('posts')
