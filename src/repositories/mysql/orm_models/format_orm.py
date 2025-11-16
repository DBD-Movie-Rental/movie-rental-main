from sqlalchemy import Column, Integer, String
from .base import Base


class Format(Base):
    __tablename__ = "format"

    format_id = Column(Integer, primary_key=True, autoincrement=True)
    format = Column(String(10), nullable=False, unique=True)  # ENUM('DVD','BLU-RAY','VHS')

    def to_dict(self):
        return {
            "id": self.format_id,
            "format": self.format,
        }
