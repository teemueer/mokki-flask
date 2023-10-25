import os
from flask_mqtt import ssl

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "teemu")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MQTT_BROKER_URL = os.environ.get("MQTT_BROKER_URL", "debian.local")
    MQTT_BROKER_PORT = 8883
    MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "")
    MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
    MQTT_KEEPALIVE = 5
    MQTT_TLS_CA_CERTS = os.environ.get("MQTT_TLS_CA_CERTS", "/home/teemu/certs/ca.crt")
    MQTT_TLS_ENABLED = True
    MQTT_TLS_VERSION = ssl.PROTOCOL_TLSv1_2


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
