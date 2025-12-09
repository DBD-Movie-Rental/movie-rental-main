from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.location_ogm import Location


class LocationRepository(Neo4jBaseRepository[Location]):
    def __init__(self):
        super().__init__(Location, id_field="locationId")
