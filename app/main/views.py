# -*- coding: utf-8 -*-

from . import main
from ..models import Book, Github, SegmentFault
from flask import render_template


@main.route('/')
def index():
    books = Book.query.all()
    projects = Github.query.limit(15).all()
    segments = SegmentFault.query.limit(15).all()
    return render_template('book/index.html', books=books, projects=projects,
                           segments=segments)