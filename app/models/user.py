from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

from .base import BaseModel
from app import db
from app.models.room import RoomModel


class UserModel(BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    rooms = db.relationship("RoomModel", backref="user", lazy="joined")

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def get_token(self) -> str:
        access_token = create_access_token(identity=self.id)
        return access_token

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()
