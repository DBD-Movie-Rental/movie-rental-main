from mongoengine import Document, IntField, StringField, Decimal128Field as DecimalField


class FeeTypeDocument(Document):
    meta = {
        "collection": "feeTypes",
        "auto_create_index": False,
    }

    fee_id = IntField(required=True, unique=True, db_field="feeId")
    fee_type = StringField(
        required=True,
        choices=("LATE", "DAMAGED", "OTHER"),
        db_field="feeType",
    )
    default_amount_dkk = DecimalField(required=True, db_field="defaultAmountDkk")

    def to_dict(self) -> dict:
        return {
            "id": self.fee_id,
            "fee_type": self.fee_type,
            "default_amount_dkk": str(self.default_amount_dkk)
            if self.default_amount_dkk is not None
            else None,
        }
