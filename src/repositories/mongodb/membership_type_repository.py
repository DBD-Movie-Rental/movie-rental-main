from .base_repository import MongoBaseRepository
from .odm_models.membership_type_document import MembershipTypeDocument


class MembershipTypeRepositoryMongo(MongoBaseRepository[MembershipTypeDocument]):
    def __init__(self) -> None:
        super().__init__(MembershipTypeDocument, id_field="membership_id")
