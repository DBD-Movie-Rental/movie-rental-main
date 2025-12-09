from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.membership_plan_ogm import MembershipPlan


class MembershipPlanRepository(Neo4jBaseRepository[MembershipPlan]):
    def __init__(self):
        super().__init__(MembershipPlan, id_field="membershipPlanId")
