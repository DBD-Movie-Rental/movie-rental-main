from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.membership_ogm import Membership


class MembershipRepository(Neo4jBaseRepository[Membership]):
    def __init__(self):
        super().__init__(Membership, id_field="membershipId")
