import json

from .base import BaseModel
from app import db, mqtt


class DeviceModel(BaseModel):
    __tablename__ = "devices"
    __table_args__ = (
        db.UniqueConstraint("name", "room_id", name="unique_name_per_room"),
    )

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    temperature = db.Column(db.Integer)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))

    @classmethod
    def find_by_uid(cls, uid: str) -> "DeviceModel":
        return cls.query.filter_by(uid=uid).first()

    @classmethod
    def find_by_name(cls, name: str) -> "DeviceModel":
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all_by_room_id(cls, room_id: int):
        return cls.query.filter_by(room_id=room_id).all()

    def set_temperature(self, temperature):
        data = {"set_temperature": str(temperature)}
        mqtt.publish(f"command/{self.uid}", json.dumps(data))
        self.temperature = temperature
        self.save_to_db()
