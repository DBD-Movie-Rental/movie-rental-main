from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.rental_ogm import Rental


class RentalRepository(Neo4jBaseRepository[Rental]):
    def __init__(self):
        super().__init__(Rental, id_field="rentalId")
