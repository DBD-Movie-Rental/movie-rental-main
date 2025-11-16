from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base


class Address(Base):
    __tablename__ = "address"

    address_id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    post_code = Column(String(4), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.address_id,
            "address": self.address,
            "city": self.city,
            "post_code": self.post_code,
            "customer_id": self.customer_id,
        }
