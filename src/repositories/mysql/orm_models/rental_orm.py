from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from .base import Base


class Rental(Base):
    __tablename__ = "rental"

    rental_id = Column(Integer, primary_key=True, autoincrement=True)
    rented_at_datetime = Column(DateTime, nullable=True)
    returned_at_datetime = Column(DateTime, nullable=True)
    due_at_datetime = Column(DateTime, nullable=True)
    reserved_at_datetime = Column(DateTime, nullable=True)
    status = Column(Enum("RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id", onupdate="CASCADE"), nullable=False)
    promo_code_id = Column(Integer, ForeignKey("promo_code.promo_code_id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employee.employee_id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    def to_dict(self):
        return {
            "id": self.rental_id,
            "rented_at_datetime": self.rented_at_datetime.isoformat() if self.rented_at_datetime else None,
            "returned_at_datetime": self.returned_at_datetime.isoformat() if self.returned_at_datetime else None,
            "due_at_datetime": self.due_at_datetime.isoformat() if self.due_at_datetime else None,
            "reserved_at_datetime": self.reserved_at_datetime.isoformat() if self.reserved_at_datetime else None,
            "status": self.status,
            "customer_id": self.customer_id,
            "promo_code_id": self.promo_code_id,
            "employee_id": self.employee_id,
        }
