# -*- coding: utf-8 -*-

from . import blog


@blog.route('/')
def home():
    return 'blog'