from app import ma
from app.models.room import RoomModel


class RoomSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RoomModel
        load_instance = True
        include_fk = True
        dump_only = ("id",)
