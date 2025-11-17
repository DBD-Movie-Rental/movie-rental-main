from mongoengine import Document, IntField, StringField


class MembershipTypeDocument(Document):
    meta = {
        "collection": "membershipTypes",
        "auto_create_index": False,
    }

    membership_id = IntField(required=True, unique=True, db_field="membershipId")
    type = StringField(
        required=True,
        choices=("GOLD", "SILVER", "BRONZE"),
        db_field="type",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.membership_id,
            "type": self.type,
        }
