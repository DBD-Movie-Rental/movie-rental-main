from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.inventory_item_ogm import InventoryItem


class InventoryItemRepository(Neo4jBaseRepository[InventoryItem]):
    def __init__(self):
        super().__init__(InventoryItem, id_field="inventoryItemId")
