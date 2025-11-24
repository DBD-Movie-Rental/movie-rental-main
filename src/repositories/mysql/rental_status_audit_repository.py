from typing import List, Dict, Any, Optional
from sqlalchemy import select
from .base_repository import BaseRepository
from .orm_models.rental_status_audit_orm import RentalStatusAudit

class RentalStatusAuditRepository(BaseRepository[RentalStatusAudit]):
    def __init__(self):
        super().__init__(RentalStatusAudit)

    def list(self, rental_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self._SessionLocal() as session:
            stmt = select(RentalStatusAudit).order_by(RentalStatusAudit.audit_id.desc()).limit(limit)
            if rental_id is not None:
                stmt = select(RentalStatusAudit).where(RentalStatusAudit.rental_id == rental_id).order_by(RentalStatusAudit.audit_id.desc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [r.to_dict() for r in rows]
