from typing import List, Dict, Any, Optional
from sqlalchemy import select
from .base_repository import BaseRepository
from .orm_models.payment_audit_orm import PaymentAudit

class PaymentAuditRepository(BaseRepository[PaymentAudit]):
    def __init__(self):
        super().__init__(PaymentAudit)

    def list(self, payment_id: Optional[int] = None, rental_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self._SessionLocal() as session:
            stmt = select(PaymentAudit).order_by(PaymentAudit.audit_id.desc()).limit(limit)
            if payment_id is not None:
                stmt = select(PaymentAudit).where(PaymentAudit.payment_id == payment_id).order_by(PaymentAudit.audit_id.desc()).limit(limit)
            elif rental_id is not None:
                stmt = select(PaymentAudit).where(PaymentAudit.rental_id == rental_id).order_by(PaymentAudit.audit_id.desc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [r.to_dict() for r in rows]
