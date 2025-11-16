from sqlalchemy import Column, Integer, String
from .base import Base


class Location(Base):
    __tablename__ = "location"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.location_id,
            "address": self.address,
            "city": self.city,
        }
