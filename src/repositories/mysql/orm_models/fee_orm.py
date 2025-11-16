from sqlalchemy import Column, Integer, String, DECIMAL
from .base import Base


class Fee(Base):
    __tablename__ = "fee"

    fee_id = Column(Integer, primary_key=True, autoincrement=True)
    fee_type = Column(String(10), nullable=False, unique=True)  # ENUM('LATE','DAMAGED','OTHER')
    amount_dkk = Column(DECIMAL(10, 2), nullable=False)

    def to_dict(self):
        return {
            "id": self.fee_id,
            "fee_type": self.fee_type,
            "amount_dkk": float(self.amount_dkk) if self.amount_dkk is not None else None,
        }
