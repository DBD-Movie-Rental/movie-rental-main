from .base_repository import BaseRepository
from .orm_models.payment_orm import Payment


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self):
        super().__init__(Payment)
