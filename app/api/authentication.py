from . import api
from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g
from ..models import User
from .errors import unauthorized, forbidden


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    if username_or_token and password == '':
        user = User.verify_basic_auth_token(username_or_token)
        if user:
            g.current_user = user
            g.used_token = True
            return True
    u = User.query.filter_by(username = username_or_token).first()
    if u and u.verify_password(password):
        g.current_user = u
        g.used_token = False
        return True
    return False



@auth.error_handler
def error_handler():
    return jsonify({
        "error": "Unauthorized Access"
    })


@api.route('/token')
@auth.login_required
def get_token():
    if g.current_user and g.used_token is False:
        return jsonify({
            "token": g.current_user.generate_basic_auth_token(3600),
            "expires": 3600,
            "username": auth.username()
        })
    return unauthorized('invalid')


@api.before_request
@auth.login_required
def login_required():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('unconfirmed account')
