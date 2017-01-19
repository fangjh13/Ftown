#! -*- coding: utf-8 -*-


from flask import Flask
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from .main import main
    app.register_blueprint(main, url_prefix='/')

    return app