from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.payment_ogm import Payment


class PaymentRepository(Neo4jBaseRepository[Payment]):
    def __init__(self):
        super().__init__(Payment, id_field="paymentId")
