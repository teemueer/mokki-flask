import uuid

from .base import BaseModel
from app import db


class DeviceModel(BaseModel):
    __tablename__ = "devices"
    __table_args__ = (
        db.UniqueConstraint("name", "room_id", name="unique_name_per_room"),
    )

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(
        db.String(64), unique=True, nullable=False, default=str(uuid.uuid4())
    )
    name = db.Column(db.String(128), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))

    @classmethod
    def find_by_uid(cls, uid: str) -> "DeviceModel":
        return cls.query.filter_by(uid=uid).first()

    @classmethod
    def find_by_name(cls, name: str) -> "DeviceModel":
        return cls.query.filter_by(name=name).first()
