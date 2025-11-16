from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Payment(Base):
    __tablename__ = "payment"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    amount_dkk = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    rental_id = Column(Integer, ForeignKey("rental.rental_id", onupdate="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.payment_id,
            "amount_dkk": float(self.amount_dkk) if self.amount_dkk is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "rental_id": self.rental_id,
        }
