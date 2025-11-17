from .base_repository import MongoBaseRepository
from .odm_models.promo_code_document import PromoCodeDocument


class PromoCodeRepositoryMongo(MongoBaseRepository[PromoCodeDocument]):
    def __init__(self) -> None:
        super().__init__(PromoCodeDocument, id_field="promo_code_id")
