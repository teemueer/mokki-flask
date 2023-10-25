from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta

from app.models.device import DeviceModel
from app.schemas.device import DeviceSchema

UNIQUE_ID_ALREADY_EXISTS = "A device with unique ID '{}' already exists."
NAME_ALREADY_EXISTS = "A device with name '{}' already exists."
ERROR_INSERTING = "An error occured while inserting the device."
DEVICE_NOT_FOUND = "Device not found."
DEVICE_DELETED = "Device deleted."

device_schema = DeviceSchema()
device_list_schema = DeviceSchema(many=True)


class Device(Resource):
    @classmethod
    def get(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device:
            return {"message": DEVICE_NOT_FOUND}, 404
        return device_schema.dump(device), 200

    @classmethod
    @jwt_required()
    def delete(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device:
            return {"message": DEVICE_NOT_FOUND}, 404

        device.delete_from_db()
        return {"message": DEVICE_DELETED}, 200

    @classmethod
    @jwt_required()
    def put(cls, device_id: int):
        device_json = request.get_json()
        device = DeviceModel.find_by_id(device_id)

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
    def get(cls):
        devices = device_list_schema.dump(DeviceModel.find_all())
        return {"devices": devices}, 200


class DeviceRegister(Resource):
    @classmethod
    #@jwt_required()
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

class DeviceCertificate(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        print(get_jwt_identity())