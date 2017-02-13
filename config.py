#! -*- coding: utf-8 -*-

import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'qRk5fpfYwY5K22ci/l3/Ig=='
    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ftown:fangjh13@localhost/ftown'
    SQLALCHEMY_TRACK_MODIFICATIONS = True



class TestingConfig(Config):
    DEBUG = True
    pass


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}