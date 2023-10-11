import os
from flask_mqtt import ssl

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'salainen-avain'

    MQTT_BROKER_URL = 'localhost'
    MQTT_BROKER_PORT = 8883
    MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
    MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = True
    MQTT_TLS_CA_CERTS = '/etc/mosquitto/certs/mosquitto.crt'
    MQTT_TLS_VERSION = ssl.PROTOCOL_TLSv1_2

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    #DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
