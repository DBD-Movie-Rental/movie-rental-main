from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import sessionmaker

from .orm_models.base import SessionLocal


ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Generic repository with common CRUD helpers.

    By default, returns dictionaries using a model's `to_dict()` if available,
    otherwise a best-effort dict of the column attributes.
    """

    def __init__(self, model: Type[ModelT], session_factory: sessionmaker = SessionLocal):
        self.model = model
        self._SessionLocal = session_factory

    # ── public helpers ──────────────────────────────────────────────────────
    def get_all(self) -> List[Dict[str, Any]]:
        with self._SessionLocal() as session:
            rows = session.query(self.model).all()
            return [self._to_dict(row) for row in rows]

    def get_by_id(self, id_: Any) -> Optional[Dict[str, Any]]:
        with self._SessionLocal() as session:
            obj = session.get(self.model, id_)
            return self._to_dict(obj) if obj else None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._SessionLocal() as session:
            obj = self.model(**data)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return self._to_dict(obj)

    def update(self, id_: Any, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with self._SessionLocal() as session:
            obj = session.get(self.model, id_)
            if not obj:
                return None
            for k, v in data.items():
                if hasattr(obj, k):
                    setattr(obj, k, v)
            session.commit()
            session.refresh(obj)
            return self._to_dict(obj)

    def delete(self, id_: Any) -> bool:
        with self._SessionLocal() as session:
            obj = session.get(self.model, id_)
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True

    # ── utilities ──────────────────────────────────────────────────────────
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        if obj is None:
            return {}
        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()
        # Fallback: best-effort conversion excluding SQLAlchemy internals
        raw = {k: v for k, v in vars(obj).items() if not k.startswith("_")}
        # Convert decimals/datetimes if needed (keep simple here)
        return raw
