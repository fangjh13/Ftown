# -*- coding: utf-8 -*-

from . import blog
from flask import make_response, jsonify, request, redirect, url_for


@blog.app_errorhandler(404)
def not_found(e):
    print(request.accept_mimetypes)
    if request.accept_mimetypes.accept_json and \
        not request.accept_mimetypes.accept_html:
        response = make_response(jsonify({'error': 'not found'}))
        response.status_code = 404
        return response
    return redirect(url_for('blog.home')), 404