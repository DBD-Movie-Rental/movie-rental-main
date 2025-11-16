from sqlalchemy import Column, Integer, String
from .base import Base


class Genre(Base):
    __tablename__ = "genre"

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.genre_id,
            "name": self.name,
        }
