from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.promo_code_ogm import PromoCode


class PromoCodeRepository(Neo4jBaseRepository[PromoCode]):
    def __init__(self):
        super().__init__(PromoCode, id_field="promoCodeId")
