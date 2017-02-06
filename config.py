#! -*- coding: utf-8 -*-

class Config(object):
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ftown:fangjh13@localhost/ftown'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}