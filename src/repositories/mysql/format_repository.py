from .base_repository import BaseRepository
from .orm_models.format_orm import Format


class FormatRepository(BaseRepository[Format]):
    def __init__(self):
        super().__init__(Format)
