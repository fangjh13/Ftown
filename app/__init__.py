#! -*- coding: utf-8 -*-


from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_mail import Mail
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
moment = Moment()
mail = Mail()
bootstrap = Bootstrap()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    from .main import main
    app.register_blueprint(main, url_prefix='/')

    from .blog import blog
    app.register_blueprint(blog, url_prefix='/blog')

    return app