from .base import BaseModel
from app import db


class DeviceModel(BaseModel):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(64), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_unique_id(cls, unique_id: str) -> "DeviceModel":
        return cls.query.filter_by(unique_id=unique_id).first()

    @classmethod
    def find_by_name(cls, name: str) -> "DeviceModel":
        return cls.query.filter_by(name=name).first()
