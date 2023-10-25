from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_mqtt import Mqtt

from config import config
from app.handlers.error_handlers import validation_error

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()
mqtt = Mqtt()


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    from app.resources.user import UserRegister, UserLogin, UserLogout, User

    from app.resources.device import DeviceRegister, DeviceToken, DeviceCertificate, DeviceList, Device

    api = Api(app)

    api.add_resource(UserRegister, "/register")
    api.add_resource(UserLogin, "/login")
    api.add_resource(UserLogout, "/logout")

    api.add_resource(User, "/users/<int:user_id>")

    api.add_resource(DeviceRegister, "/devices/register/<string:unique_id>")
    api.add_resource(DeviceToken, "/devices/token/<string:unique_id>")
    api.add_resource(DeviceCertificate, "/devices/certificate")
    api.add_resource(DeviceList, "/devices")
    api.add_resource(Device, "/devices/<int:device_id>")

    app.register_error_handler(400, validation_error)

    from app.handlers import mqtt_handlers

    mqtt.init_app(app)

    return app
