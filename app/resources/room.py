from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from app.models.room import RoomModel
from app.schemas.room import RoomSchema

NAME_ALREADY_EXISTS = "A room with name '{}' already exists."
ERROR_INSERTING = "An error occured while inserting the room."
ROOM_NOT_FOUND = "Room not found."
ROOM_DELETED = "Room deleted."

room_schema = RoomSchema()
room_list_schema = RoomSchema(many=True)


class Room(Resource):
    @classmethod
    @jwt_required()
    def get(cls, room_id: int):
        room = RoomModel.find_by_id(room_id)
        if not room or room.user_id != get_jwt_identity():
            return {"message": ROOM_NOT_FOUND}, 404

        return room_schema.dump(room), 200

    @classmethod
    @jwt_required()
    def delete(cls, room_id: int):
        room = RoomModel.find_by_id(room_id)
        if not room or room.user_id != get_jwt_identity():
            return {"message": ROOM_NOT_FOUND}, 404

        room.delete_from_db()

        return {"message": ROOM_DELETED}, 200


class RoomList(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        user_id = get_jwt_identity()
        rooms = RoomModel.query.filter_by(user_id=user_id).all()
        return room_list_schema.dump(rooms), 200

    @classmethod
    @jwt_required()
    def post(cls):
        room_json = request.get_json()
        room_json["user_id"] = get_jwt_identity()

        room = room_schema.load(room_json)

        try:
            room.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 400

        return room_schema.dump(room), 201
