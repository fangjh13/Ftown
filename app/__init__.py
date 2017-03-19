#! -*- coding: utf-8 -*-


from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pagedown import PageDown


db = SQLAlchemy()
moment = Moment()
mail = Mail()
bootstrap = Bootstrap()
login_manager = LoginManager()
pagedown = PageDown()

login_manager.login_view = "auth.login"
login_manager.login_message = "用户未登录，请先登录"

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)


    db.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main
    app.register_blueprint(main)

    from .blog import blog
    app.register_blueprint(blog, url_prefix='/blog')

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    return app