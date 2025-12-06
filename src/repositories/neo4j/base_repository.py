from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

# Ensure neomodel is configured via side-effect import
from . import connection  # noqa: F401

from neomodel import StructuredNode
from neomodel.exceptions import DoesNotExist, MultipleNodesReturned


NodeT = TypeVar("NodeT", bound=StructuredNode)


class Neo4jBaseRepository(Generic[NodeT]):
    """
    Generic repository for neomodel StructuredNode OGM models.

    Mirrors the style of the SQL and Mongo repositories:
      - constructor takes a model and a logical id field name (e.g. "customerId")
      - CRUD helpers return plain dicts, using model.to_dict() if available
    Notes:
      - This base focuses on node properties only (no relationship mutations).
    """

    def __init__(self, model: Type[NodeT], id_field: str = "id"):
        self.model = model
        self.id_field = id_field  # e.g., "customerId"

    # ── public helpers ────────────────────────────────────────────
    def get_all(self) -> List[Dict[str, Any]]:
        nodes = self.model.nodes.all()
        return [self._to_dict(n) for n in nodes]

    def get_by_id(self, id_: Any) -> Optional[Dict[str, Any]]:
        try:
            node = self.model.nodes.get(**{self.id_field: id_})
        except (DoesNotExist, MultipleNodesReturned):
            return None
        return self._to_dict(node)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # For Neo4j we do not simulate auto-increment. Expect caller to supply ids when required.
        node = self.model(**data).save()
        return self._to_dict(node)

    def update(self, id_: Any, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            node = self.model.nodes.get(**{self.id_field: id_})
        except (DoesNotExist, MultipleNodesReturned):
            return None

        # Update only known property attributes; relationships should be handled explicitly in subclasses.
        for k, v in data.items():
            if hasattr(node, k):
                try:
                    setattr(node, k, v)
                except Exception:
                    # Ignore relationship or invalid assignments here
                    pass
        node.save()
        return self._to_dict(node)

    def delete(self, id_: Any) -> bool:
        try:
            node = self.model.nodes.get(**{self.id_field: id_})
        except (DoesNotExist, MultipleNodesReturned):
            return False
        node.delete()
        return True

    # ── utilities ────────────────────────────────────────────────
    def _to_dict(self, node: Any) -> Dict[str, Any]:
        if node is None:
            return {}
        # Prefer a custom serializer if the model provides one
        if hasattr(node, "to_dict") and callable(getattr(node, "to_dict")):
            try:
                return node.to_dict()  # type: ignore
            except Exception:
                pass

        # Try neomodel properties dict first
        props: Dict[str, Any] | None = None
        if hasattr(node, "__properties__"):
            try:
                # __properties__ contains node properties excluding relationships
                props = dict(getattr(node, "__properties__"))  # type: ignore[arg-type]
            except Exception:
                props = None

        if props is None:
            # Fallback: use class-defined property names if available
            prop_names: List[str] = []
            try:
                # defined_properties may exist on neomodel StructuredNode (class-level)
                defined = node.__class__.defined_properties(rels=False, aliases=False)
                prop_names = list(defined.keys())  # type: ignore[assignment]
            except Exception:
                # Last resort: best-effort reflection (skip callables/private)
                prop_names = [
                    n for n in dir(node)
                    if not n.startswith("_") and not callable(getattr(node, n, None))
                ]
            props = {n: getattr(node, n, None) for n in prop_names}

        return props
