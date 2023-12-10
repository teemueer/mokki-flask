import asyncio
import os
import json
import uuid
from bleak import BleakScanner, BleakClient
from flask import request, current_app
from flask_restx import Resource, reqparse, Api
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from tpm2_pytss import *
from tpm2_pytss.constants import TPM2_ALG

from app.models.device import DeviceModel
from app.models.room import RoomModel
from app.models.uid import UidModel
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

api = Api()


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

        room_id = device_json.get("room_id")
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


async def handle_response(sender, data, data_queue):
    tpm = ESAPI()
    persistent_handle = current_app.config.get("PERSISTENT_HANDLE")
    key_handle = tpm.tr_from_tpmpublic(persistent_handle)

    data = tpm.rsa_decrypt(
        key_handle,
        TPM2B_PUBLIC_KEY_RSA(bytes(data)),
        TPMT_RSA_DECRYPT(_cdata=TPM2_ALG.RSAES),
    )
    await data_queue.put(bytes(data).decode())


async def pair_device(name, chunk_size=20):
    device = await BleakScanner.find_device_by_name(name)
    if not device:
        return

    data_queue = asyncio.Queue()

    uart_tx = current_app.config.get("UART_TX")
    uart_rx = current_app.config.get("UART_RX")

    async with BleakClient(device.address) as client:
        handler = lambda s, d: asyncio.create_task(handle_response(s, d, data_queue))
        await client.start_notify(uart_tx, handler)

        received_uuid = await data_queue.get()
        print(received_uuid)

        uid = UidModel.find_by_uid(received_uuid)
        print(uid)

        if not uid:
            return None

        await client.stop_notify(uart_tx)

        data = {
            "wlan_ssid": os.environ.get("WLAN_SSID"),
            "wlan_password": os.environ.get("WLAN_PASSWORD"),
            "mqtt_broker_url": os.environ.get("MQTT_BROKER_URL"),
            "uuid": uid.uid,
        }

        data = json.dumps(data).encode() + b"\0"
        chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

        for chunk in chunks:
            await client.write_gatt_char(uart_rx, chunk, response=False)

        return uid.uid


class DeviceRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name",
        type=str,
        required=True,
        help="The name comes from the QR code on the device",
    )

    @classmethod
    @api.expect(parser)
    def get(cls):
        name = request.args.get("name")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        uid = loop.run_until_complete(pair_device(name))

        if not uid:
            return {"message": ERROR_PAIRING_DEVICE}, 500

        device_json = {"uid": uid, "room_id": "1", "name": name}
        device = device_schema.load(device_json)

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 400

        return device_schema.dump(device), 201
