from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.format_ogm import Format


class FormatRepository(Neo4jBaseRepository[Format]):
    def __init__(self):
        super().__init__(Format, id_field="formatId")
