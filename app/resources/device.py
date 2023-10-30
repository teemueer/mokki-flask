from flask import request
from flask_restful import Resource
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
class DeviceRegister(Resource):
    @classmethod
    # @jwt_required()
    def get(cls, unique_id: str):
        device = DeviceModel.find_by_unique_id(unique_id=unique_id)
        if device:
            return {"message": UNIQUE_ID_ALREADY_EXISTS.format(unique_id)}, 400

        device = device_schema.load({"unique_id": unique_id})

        try:
            device.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return device_schema.dump(device), 201


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
