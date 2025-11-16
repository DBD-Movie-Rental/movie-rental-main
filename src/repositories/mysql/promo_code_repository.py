from .base_repository import BaseRepository
from .orm_models.promo_code_orm import PromoCode


class PromoCodeRepository(BaseRepository[PromoCode]):
    def __init__(self):
        super().__init__(PromoCode)
