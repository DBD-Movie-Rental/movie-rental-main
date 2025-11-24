from sqlalchemy import Column, Integer, DECIMAL, Enum, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class PaymentAudit(Base):
    __tablename__ = "payment_audit"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payment.payment_id"), nullable=True)
    rental_id = Column(Integer, ForeignKey("rental.rental_id"), nullable=True)
    action = Column(Enum("INSERT", "UPDATE", "DELETE", "REFUND"), nullable=False)
    old_amount_dkk = Column(DECIMAL(10,2), nullable=True)
    new_amount_dkk = Column(DECIMAL(10,2), nullable=True)
    changed_by = Column(String(128), nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    def to_dict(self):
        return {
            "audit_id": self.audit_id,
            "payment_id": self.payment_id,
            "rental_id": self.rental_id,
            "action": self.action,
            "old_amount_dkk": float(self.old_amount_dkk) if self.old_amount_dkk is not None else None,
            "new_amount_dkk": float(self.new_amount_dkk) if self.new_amount_dkk is not None else None,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
        }
