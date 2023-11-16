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
ERROR_PAIRING_DEVICE = "Error pairing device via bluetooth."
NAME_WAS_NOT_PROVIDED = "Name was not provided."

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
    def patch(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device or device.room.user_id != get_jwt_identity():
            return {"message": DEVICE_NOT_FOUND}, 404

        device_json = request.get_json()
        name = device_json.get("name")
        if not name:
            return {"message": NAME_WAS_NOT_PROVIDED}, 400

        device.name = name

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return device_schema.dump(device), 200


class DeviceList(Resource):
    @classmethod
    @jwt_required()
    def get(cls, room_id: int):
        room = RoomModel.find_by_id(room_id)

        if not room or room.user_id != get_jwt_identity():
            return {"message": ROOM_NOT_FOUND_OR_NO_ACCESS}, 404

        devices = DeviceModel.find_all()
        return device_list_schema.dump(devices), 200


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

class DeviceRegister(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        name = request.args.get("name")
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            uid = loop.run_until_complete(send_credentials(name))
        except:
            return {"message": ERROR_PAIRING_DEVICE}, 404

        device_json = {"uid": uid, "room_id": "1", "name": name}
        device = device_schema.load(device_json)

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 400

        return device_schema.dump(device), 201

