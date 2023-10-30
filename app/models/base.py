from typing import List, Self

from app import db


class BaseModel(db.Model):
    __abstract__ = True

    @classmethod
    def find_by_id(cls, _id: int) -> Self:
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List[Self]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
