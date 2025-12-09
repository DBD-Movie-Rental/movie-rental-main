from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.address_ogm import Address


class AddressRepository(Neo4jBaseRepository[Address]):
    def __init__(self):
        super().__init__(Address, id_field="addressId")
