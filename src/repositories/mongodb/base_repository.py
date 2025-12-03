# src/repositories/mongodb/base_repository.py
from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from mongoengine import Document

DocT = TypeVar("DocT", bound=Document)


class MongoBaseRepository(Generic[DocT]):
    """
    Generic repository for MongoEngine Documents.

    Assumes:
      - the model has a .to_dict() method returning a serializable dict
      - lookups are by a logical ID field (e.g. "customer_id").
    """

    def __init__(self, model: Type[DocT], id_field: str = "id"):
        self.model = model
        self.id_field = id_field  # e.g. "customer_id"

    # ── public helpers ────────────────────────────────────────────
    def get_all(self) -> List[Dict[str, Any]]:
        docs = self.model.objects()  # MongoEngine QuerySet
        return [self._to_dict(doc) for doc in docs]

    def get_by_id(self, id_: Any) -> Optional[Dict[str, Any]]:
        doc = self.model.objects(**{self.id_field: id_}).first()
        return self._to_dict(doc) if doc else None

    def _get_next_id(self) -> int:
        """
        Helper to simulate auto-increment IDs.
        Finds the max existing ID and adds 1.
        """
        last = self.model.objects.order_by(f"-{self.id_field}").first()
        if last:
            return getattr(last, self.id_field) + 1
        return 1

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # If ID is missing and looks like we need an int ID, generate it
        if self.id_field not in data:
             # Check if the model's id field is an IntField
             # (This is a bit hacky, assuming we want auto-increment for all)
             data[self.id_field] = self._get_next_id()

        doc = self.model(**data)
        doc.save()
        return self._to_dict(doc)

    def update(self, id_: Any, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        doc = self.model.objects(**{self.id_field: id_}).first()
        if not doc:
            return None

        # naive field update – skip unknown attributes
        for k, v in data.items():
            if hasattr(doc, k):
                setattr(doc, k, v)

        doc.save()
        return self._to_dict(doc)

    def delete(self, id_: Any) -> bool:
        deleted_count = self.model.objects(**{self.id_field: id_}).delete()
        return deleted_count > 0

    # ── utilities ────────────────────────────────────────────────
    def _to_dict(self, doc: Any) -> Dict[str, Any]:
        if doc is None:
            return {}
        if hasattr(doc, "to_dict") and callable(doc.to_dict):
            return doc.to_dict()

        # Fallback: strip mongoengine internals
        raw = {
            k: v
            for k, v in doc.to_mongo().items()
            if not k.startswith("_")
        }
        return raw
