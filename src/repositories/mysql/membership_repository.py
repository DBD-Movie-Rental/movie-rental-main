from .base_repository import BaseRepository
from .orm_models.membership_orm import Membership


class MembershipRepository(BaseRepository[Membership]):
    def __init__(self):
        super().__init__(Membership)
