from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey
from .base import Base


class MembershipPlan(Base):
    __tablename__ = "membership_plan"

    membership_plan_id = Column(Integer, primary_key=True, autoincrement=True)
    monthly_cost = Column(DECIMAL(10, 2), nullable=False)
    starts_on = Column(DateTime, nullable=False)
    ends_on = Column(DateTime, nullable=False)
    membership_id = Column(Integer, ForeignKey("membership.membership_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "id": self.membership_plan_id,
            "monthly_cost": float(self.monthly_cost) if self.monthly_cost is not None else None,
            "starts_on": self.starts_on.isoformat() if self.starts_on else None,
            "ends_on": self.ends_on.isoformat() if self.ends_on else None,
            "membership_id": self.membership_id,
            "customer_id": self.customer_id,
        }
