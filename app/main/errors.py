# -*- coding: utf-8 -*-

from . import main
from flask import make_response, jsonify, request, redirect, url_for


@main.app_errorhandler(404)
def not_found(e):
    if 'application/json' in request.accept_mimetypes and \
        not 'txt/html' in request.accept_mimetypes:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return redirect(url_for('blog.home'))


@main.app_errorhandler(500)
def internal_server_error(e):
    if 'application/json' in request.accept_mimetypes and \
        not 'txt/html' in request.accept_mimetypes:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
