#! -*- coding: utf-8 -*-

import os


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'qRk5fpfYwY5K22ci/l3/Ig=='
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://{}:{}@localhost/ftown'.format(
            os.getenv('FTOWNUSER'), os.getenv('FTOWNPASSWD'))
    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False



class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://{}:{}@localhost/ftown_test'.format(
            os.getenv('FTOWNUSER'), os.getenv('FTOWNPASSWD'))
    WTF_CSRF_ENABLED = False
    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    # MAIL_SUPPRESS_SEND = False


class ProductionConfig(Config):
    MAIL_SERVER = "smtp.gmail.com"
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://{}:{}@localhost/ftown'.format(
            os.getenv('FTOWNUSER'), os.getenv('FTOWNPASSWD'))
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}