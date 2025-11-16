from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime
from .base import Base


class PromoCode(Base):
    __tablename__ = "promo_code"

    promo_code_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    percent_off = Column(DECIMAL(5, 2), nullable=True)
    amount_off_dkk = Column(DECIMAL(10, 2), nullable=True)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.promo_code_id,
            "code": self.code,
            "description": self.description,
            "percent_off": float(self.percent_off) if self.percent_off is not None else None,
            "amount_off_dkk": float(self.amount_off_dkk) if self.amount_off_dkk is not None else None,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
        }
