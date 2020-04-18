#! -*- coding: utf-8 -*-

import os


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'qRk5fpfYwY5K22ci/l3/Ig=='
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    REDIS_URL = "redis://@localhost:6379/1"

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
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')


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
    ELASTICSEARCH_URL = "http://localhost:19200"
    # MAIL_SUPPRESS_SEND = False


class ProductionConfig(Config):
    # gmail
    # MAIL_SERVER = "smtp.gmail.com"
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://{}:{}@localhost/ftown'.format(
            os.getenv('FTOWNUSER'), os.getenv('FTOWNPASSWD'))
    # gmail
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USE_SSL = False

    # 国内用163
    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email error to the administrators
        import logging
        from logging.handlers import SMTPHandler
        secure = None
        credentials = None
        if getattr(cls, 'MAIL_USERNAME', None):
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr="Blog Admin <{0}>".format(cls.MAIL_USERNAME),
            toaddrs=['616960344@qq.com'],
            subject='[Blog] Application Error',
            credentials=credentials,
            secure=secure,
            timeout=10)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        # TimeRotatingFileHandler
        from logging.handlers import TimedRotatingFileHandler
        time_rotating_handler = TimedRotatingFileHandler(
            filename='log/time_rotating_warning.log',
            when='D',
            backupCount=7,
            encoding='utf-8',
            utc=True
        )
        time_rotating_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        time_rotating_handler.setFormatter(formatter)
        app.logger.addHandler(time_rotating_handler)

        # handler proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
