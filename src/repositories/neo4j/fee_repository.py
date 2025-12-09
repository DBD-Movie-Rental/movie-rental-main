from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.fee_ogm import Fee


class FeeRepository(Neo4jBaseRepository[Fee]):
    def __init__(self):
        super().__init__(Fee, id_field="feeId")
