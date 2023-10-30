from marshmallow import fields

from app import ma
from app.models.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        load_only = ("password",)
        dump_only = ("id",)

        rooms = fields.Nested("RoomSchema", many=True, only=["id", "name"])
