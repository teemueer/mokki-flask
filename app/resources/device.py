import asyncio
import os
import json
import uuid
from bleak import BleakScanner, BleakClient
from flask import request, current_app
from flask_restx import Resource, reqparse
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
TEMPERATURE_WAS_NOT_PROVIDED = "Temperature was not provided."
TEMPERATURE_BETWEEN = "Temperature must be set between 0 and 40."
TEMPERATURES_SET_IN_ROOM = "Temperatures set to {} in room '{}'."
DEVICES_NOT_FOUND = "Devices not found."
DEVICE_TEMPERATURE_SET = "Device '{}' temperature set to {}."

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

        room_id = device_json("room_id")
        if room_id:
            room = RoomModel.find_by_id(room_id)
            if room and room.user_id == get_jwt_identity():
                device.room_id = room.id

        device.name = device_json.get("name", device.name)

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return device_schema.dump(device), 200
    
    @classmethod
    @jwt_required()
    def post(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device or device.room.user_id != get_jwt_identity():
            return {"message": DEVICE_NOT_FOUND}, 404
        
        device_json = request.get_json()
        temperature = device_json.get("temperature")
        if not temperature:
            return {"message": TEMPERATURE_WAS_NOT_PROVIDED}, 400

        temperature = int(temperature)
        min_temperature = current_app.config.get("MIN_TEMPERATURE")
        max_temperature = current_app.config.get("MAX_TEMPERATURE")
        if min_temperature >= temperature >= max_temperature:
            return {"message": TEMPERATURE_BETWEEN}, 400

        device.set_temperature(temperature)

        return {"message": DEVICE_TEMPERATURE_SET.format(device.name, temperature)}


class DeviceList(Resource):
    @classmethod
    @jwt_required()
    def get(cls, room_id: int):
        room = RoomModel.find_by_id(room_id)

        if not room or room.user_id != get_jwt_identity():
            return {"message": ROOM_NOT_FOUND_OR_NO_ACCESS}, 404

        devices = DeviceModel.find_all_by_room_id(room_id)
        return device_list_schema.dump(devices), 200

    @classmethod
    @jwt_required()
    def post(cls, room_id: int):
        room = RoomModel.find_by_id(room_id)

        if not room or room.user_id != get_jwt_identity():
            return {"message": ROOM_NOT_FOUND_OR_NO_ACCESS}, 404

        device_json = request.get_json()
        temperature = device_json.get("temperature")
        if not temperature:
            return {"message": TEMPERATURE_WAS_NOT_PROVIDED}, 400

        temperature = int(temperature)
        min_temperature = current_app.config.get("MIN_TEMPERATURE")
        max_temperature = current_app.config.get("MAX_TEMPERATURE")
        if min_temperature >= temperature >= max_temperature:
            return {"message": TEMPERATURE_BETWEEN}, 400

        devices = DeviceModel.find_all_by_room_id(room_id)
        if not devices:
            return {"message": DEVICES_NOT_FOUND}, 400

        for device in devices:
            device.set_temperature(temperature)

        return {"message": TEMPERATURES_SET_IN_ROOM.format(temperature, room.name)}


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
