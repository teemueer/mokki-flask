from .base import BaseModel
from app import db


class RoomModel(BaseModel):
    __tablename__ = "rooms"
    __table_args__ = (
        db.UniqueConstraint("name", "user_id", name="unique_name_per_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    devices = db.relationship("DeviceModel", backref="room", lazy=True)

    @classmethod
    def find_by_name(cls, name: str) -> "RoomModel":
        return cls.query.filter_by(name=name).first()
