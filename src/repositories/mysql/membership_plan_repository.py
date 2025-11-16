from .base_repository import BaseRepository
from .orm_models.membership_plan_orm import MembershipPlan


class MembershipPlanRepository(BaseRepository[MembershipPlan]):
    def __init__(self):
        super().__init__(MembershipPlan)
