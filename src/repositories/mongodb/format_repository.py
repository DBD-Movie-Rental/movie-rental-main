from .base_repository import MongoBaseRepository
from .odm_models.format_document import FormatDocument


class FormatRepositoryMongo(MongoBaseRepository[FormatDocument]):
    def __init__(self) -> None:
        super().__init__(FormatDocument, id_field="format_id")
