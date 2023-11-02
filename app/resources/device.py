import asyncio
import os
import json
import uuid
from bleak import BleakScanner, BleakClient
from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app.models.device import DeviceModel
from app.models.room import RoomModel
from app.schemas.device import DeviceSchema

UNIQUE_ID_ALREADY_EXISTS = "A device with unique ID '{}' already exists."
NAME_ALREADY_EXISTS = "A device with name '{}' already exists."
ERROR_INSERTING = "An error occured while inserting the device."
DEVICE_NOT_FOUND = "Device not found."
DEVICE_DELETED = "Device deleted."
ROOM_NOT_FOUND_OR_NO_ACCESS = "Room not found or you don't have access to it."

device_schema = DeviceSchema()
device_list_schema = DeviceSchema(many=True)


class Device(Resource):
    @classmethod
    @jwt_required()
    def get(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device or device.room.user_id != get_jwt_identity():
            return {"message": DEVICE_NOT_FOUND}, 404

        return device_schema.dump(device), 200

    @classmethod
    @jwt_required()
    def delete(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device or device.room.user_id != get_jwt_identity():
            return {"message": DEVICE_NOT_FOUND}, 404

        device.delete_from_db()

        return {"message": DEVICE_DELETED}, 200

    @classmethod
    @jwt_required()
    def put(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device or device.room.user_id != get_jwt_identity():
            return {"message": DEVICE_NOT_FOUND}, 404

        device_json = request.get_json()

        if device:
            device.name = device_json["name"]
            status_code = 200
        else:
            device = device_schema.load(device_json)
            status_code = 201

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return device_schema.dump(device), status_code


class DeviceList(Resource):
    @classmethod
    @jwt_required()
    def get(cls, room_id: int):
        room = RoomModel.find_by_id(room_id)

        if not room or room.user_id != get_jwt_identity():
            return {"message": ROOM_NOT_FOUND_OR_NO_ACCESS}, 404

        devices = DeviceModel.find_all()
        return device_list_schema.dump(devices), 200

"""
    @classmethod
    @jwt_required()
    def post(cls, room_id: int):
        room = RoomModel.find_by_id(room_id)

        if not room or room.user_id != get_jwt_identity():
            return {"message": ROOM_NOT_FOUND_OR_NO_ACCESS}, 404

        device_json = request.get_json()
        device_json["room_id"] = room.id

        device = device_schema.load(device_json)

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 400

        return device_schema.dump(device), 201
"""

async def send_credentials(name, chunk_size=20):
    device = await BleakScanner.find_device_by_name(name)
    if not device:
        return

    uid = str(uuid.uuid4())

    async with BleakClient(device.address) as client:
        chars = [
            char for service in client.services for char in service.characteristics
        ]
        writable_char = next(
            (char for char in chars if "write" in char.properties), None
        )

        data = {
            "wlan_ssid": os.environ.get("WLAN_SSID"),
            "wlan_password": os.environ.get("WLAN_PASSWORD"),
            "uid": uid,
            "mqtt_broker_url": os.environ.get("MQTT_BROKER_URL"),
        }

        data = json.dumps(data).encode() + b"\0"
        chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

        for chunk in chunks:
            await client.write_gatt_char(writable_char, chunk, response=False)

    return uid

loop = asyncio.get_event_loop()


class DeviceRegister(Resource):
    @classmethod
    # @jwt_required()
    def get(cls):
        name = request.args.get("name")
        uid = loop.run_until_complete(send_credentials(name))

        device_json = {"uid": uid, "room_id": "1", "name": name}
        device = device_schema.load(device_json)

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 400

        return device_schema.dump(device), 201

"""


class DeviceToken(Resource):
    @classmethod
    def get(cls, unique_id: str):
        device = DeviceModel.find_by_unique_id(unique_id=unique_id)
        if not device:
            return {"message": DEVICE_NOT_FOUND.format(unique_id)}, 400

        access_token = create_access_token(
            identity=unique_id, expires_delta=timedelta(minutes=10)
        )
        return {"access_token": access_token}, 200


"""
