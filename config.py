import os
from dotenv import load_dotenv
from flask_mqtt import ssl
from datetime import timedelta

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=365)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MQTT_BROKER_URL = os.environ.get("MQTT_BROKER_URL")
    MQTT_BROKER_PORT = 8883
    MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "")
    MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
    MQTT_KEEPALIVE = 5
    MQTT_TLS_CA_CERTS = os.environ.get("MQTT_TLS_CA_CERTS")
    MQTT_TLS_ENABLED = True
    MQTT_TLS_VERSION = ssl.PROTOCOL_TLS_CLIENT

    MIN_TEMPERATURE = 1
    MAX_TEMPERATURE = 40

    PERSISTENT_HANDLE = 0x81010021

    UART_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
    UART_RX = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
