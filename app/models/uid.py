from .base import BaseModel
from app import db


class UidModel(BaseModel):
    __tablename__ = "uids"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(64), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_uid(cls, uid):
        return cls.query.filter_by(uid=uid).first()
