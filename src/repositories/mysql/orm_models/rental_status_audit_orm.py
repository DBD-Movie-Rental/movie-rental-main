from sqlalchemy import Column, Integer, Enum, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from .base import Base

class RentalStatusAudit(Base):
    __tablename__ = "rental_status_audit"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    rental_id = Column(Integer, ForeignKey("rental.rental_id"), nullable=False)
    action = Column(Enum("INSERT", "UPDATE", "DELETE"), nullable=False)
    old_status = Column(Enum("RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"), nullable=True)
    new_status = Column(Enum("RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"), nullable=True)
    old_rented_at_datetime = Column(DateTime, nullable=True)
    new_rented_at_datetime = Column(DateTime, nullable=True)
    old_due_at_datetime = Column(DateTime, nullable=True)
    new_due_at_datetime = Column(DateTime, nullable=True)
    old_returned_at_datetime = Column(DateTime, nullable=True)
    new_returned_at_datetime = Column(DateTime, nullable=True)
    changed_by = Column(String(128), nullable=False)
    changed_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    def to_dict(self):
        return {
            "audit_id": self.audit_id,
            "rental_id": self.rental_id,
            "action": self.action,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "old_rented_at_datetime": self.old_rented_at_datetime.isoformat() if self.old_rented_at_datetime else None,
            "new_rented_at_datetime": self.new_rented_at_datetime.isoformat() if self.new_rented_at_datetime else None,
            "old_due_at_datetime": self.old_due_at_datetime.isoformat() if self.old_due_at_datetime else None,
            "new_due_at_datetime": self.new_due_at_datetime.isoformat() if self.new_due_at_datetime else None,
            "old_returned_at_datetime": self.old_returned_at_datetime.isoformat() if self.old_returned_at_datetime else None,
            "new_returned_at_datetime": self.new_returned_at_datetime.isoformat() if self.new_returned_at_datetime else None,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
        }
