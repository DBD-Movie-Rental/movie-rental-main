from sqlalchemy import Column, Integer, String
from .base import Base


class Membership(Base):
    __tablename__ = "membership"

    membership_id = Column(Integer, primary_key=True, autoincrement=True)
    membership = Column(String(10), nullable=False, unique=True)  # ENUM('GOLD','SILVER','BRONZE')

    def to_dict(self):
        return {
            "id": self.membership_id,
            "membership": self.membership,
        }
