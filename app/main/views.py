# -*- coding: utf-8 -*-

from . import main
from ..models import Book
from flask import render_template


@main.route('/')
def index():
    books = Book.query.all()
    return render_template('book/index.html', books=books)