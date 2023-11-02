from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from influxdb_client.client.query_api import QueryApi

from app.models.device import DeviceModel
from app.schemas.data import DataSchema
from app import influx_db

DEVICE_NOT_FOUND = "Device not found."

data_schema = DataSchema()
data_schema_list = DataSchema(many=True)


class Data(Resource):
    @classmethod
    @jwt_required()
    def get(cls, device_id: int):
        device = DeviceModel.find_by_id(device_id)
        if not device or device.room.user_id != get_jwt_identity():
            return {"message": DEVICE_NOT_FOUND}, 404

        args = request.args

        start_date = args.get("start_date", "-1d")
        end_date = args.get("end_date", "now()")

        query = (
            f'from(bucket: "mokki") '
            f"|> range(start: {start_date}, stop: {end_date}) "
            f'|> filter(fn: (r) => r.device == "{device.uid}") '
        )

        data_type = args.get("data_type")
        if data_type:
            if data_type not in ["temperature", "humidity", "light_level"]:
                return {"message": "Invalid data type provided"}, 400
            query += f'|> filter(fn: (r) => r["_field"] == "{data_type}")'

        query_api = influx_db.query_api()
        tables = query_api.query(query)

        data = []
        for table in tables:
            for record in table.records:
                data.append(
                    {
                        "timestamp": record.get_time(),
                        "value": record.get_value(),
                        "field": record.get_field(),
                    }
                )

        return data_schema_list.dump(data), 200
