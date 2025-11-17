from .base_repository import MongoBaseRepository
from .odm_models.fee_type_document import FeeTypeDocument


class FeeTypeRepositoryMongo(MongoBaseRepository[FeeTypeDocument]):
    def __init__(self) -> None:
        super().__init__(FeeTypeDocument, id_field="fee_id")
