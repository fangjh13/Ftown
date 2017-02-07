#! -*- coding: utf-8 -*-


from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    from .main import main
    app.register_blueprint(main, url_prefix='/')

    from .blog import blog
    app.register_blueprint(blog, url_prefix='/blog')

    return app