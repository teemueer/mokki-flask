from app import ma
from app.models.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        load_only = ("password",)
        dump_only = ("id",)
