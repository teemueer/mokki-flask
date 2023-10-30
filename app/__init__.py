import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_mqtt import Mqtt
from influxdb_client import InfluxDBClient

from config import config
from app.handlers.error_handlers import validation_error

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()
mqtt = Mqtt()

influx_db = InfluxDBClient(
    url=os.environ.get("INFLUXDB_URL"),
    token=os.environ.get("INFLUXDB_TOKEN"),
    org=os.environ.get("INFLUXDB_ORG"),
)


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    from app.resources.device import DeviceList, Device
    from app.resources.data import Data
    from app.resources.room import RoomList, Room
    from app.resources.user import UserRegister, UserLogin, UserLogout, User

    api = Api(app)

    # Rooms
    api.add_resource(RoomList, "/rooms")
    api.add_resource(Room, "/rooms/<int:room_id>")

    # Devices
    api.add_resource(DeviceList, "/rooms/<int:room_id>/devices")
    api.add_resource(Device, "/devices/<int:device_id>")
    api.add_resource(Data, "/devices/<int:device_id>/data")

    # Users
    api.add_resource(UserRegister, "/users")
    api.add_resource(UserLogin, "/auth/login")
    api.add_resource(UserLogout, "/auth/logout")
    api.add_resource(User, "/users/<int:user_id>")

    app.register_error_handler(400, validation_error)

    from app.handlers import mqtt_handlers

    if not mqtt.connected:
        mqtt.init_app(app)
        mqtt.app = app

    return app
