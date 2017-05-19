# -*- utf-8 -*-

import unittest
from manage import create_app
from app import db
from app.models import Tag, Post


class TagCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        t = Tag(name='Test_tag')
        p = Post(title='test')
        db.session.add_all([t, p])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_tag_create(self):
        t = Tag(name='Python_tag')
        db.session.add(t)
        db.session.commit()
        tags_number = Tag.query.count()
        self.assertTrue(tags_number == 2)

    def test_many_to_many_relationship(self):
        t = Tag(name='Python')
        p = Post.query.first()
        p.tags.append(t)
        db.session.add(p)
        db.session.commit()
        p1 = Post.query.first()
        self.assertTrue(p1.tags.count() == 1)
        self.assertTrue(p1.tags.first().name == 'Python')
        t1 = Tag.query.filter_by(name='Python').first()
        self.assertTrue(t1)
        self.assertTrue(t1.posts.count() == 1)

