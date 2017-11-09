# -*- coding: utf-8 -*-

from . import main
from ..models import Book, Github, SegmentFault, JueJin
from flask import render_template


@main.route('/')
def index():
    books = Book.query.all()
    projects = Github.query.limit(15).all()
    segments = SegmentFault.query.limit(15).all()
    juejins = JueJin.query.limit(15).all()
    return render_template('book/index.html', books=books, projects=projects,
                           segments=segments, juejins=juejins)


@main.route('/google000f78e215d2609a.html')
def google_verification():
    # Google site verification
    return render_template('google/google000f78e215d2609a.html')


@main.route('/baidu_verify_nxfEgFiDSN.html')
def baidu_verification():
    # baidu site verification
    return render_template('baidu/baidu_verify_nxfEgFiDSN.html')