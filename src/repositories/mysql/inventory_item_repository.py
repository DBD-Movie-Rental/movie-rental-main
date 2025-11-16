from .base_repository import BaseRepository
from .orm_models.inventory_item_orm import InventoryItem


class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(self):
        super().__init__(InventoryItem)
