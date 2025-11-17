from mongoengine import Document, IntField, StringField


class FormatDocument(Document):
    meta = {
        "collection": "formats",
        "auto_create_index": False,
    }

    format_id = IntField(required=True, unique=True, db_field="formatId")
    type = StringField(
        required=True,
        choices=("DVD", "BLU-RAY", "VHS"),
        db_field="type",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.format_id,
            "type": self.type,
        }
