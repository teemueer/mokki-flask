from app import ma
from app.models.device import DeviceModel


class DeviceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DeviceModel
        load_instance = True
        include_fk = True
        dump_only = ("id",)
