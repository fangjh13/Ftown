# -*- coding: utf-8 -*-

from . import main
from ..models import Book
from flask import render_template


@main.route('/')
def index():
    books = Book.query.order_by(Book.id.desc()).limit(5).all()
    return render_template('book/index.html')