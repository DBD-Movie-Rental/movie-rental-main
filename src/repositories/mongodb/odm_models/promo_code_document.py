from mongoengine import Document, IntField, StringField, DateTimeField, Decimal128Field as DecimalField


class PromoCodeDocument(Document):
    meta = {
        "collection": "promoCodes",
        "auto_create_index": False,
    }

    promo_code_id = IntField(required=True, unique=True, db_field="promoCodeId")
    code = StringField(required=True, db_field="code")
    description = StringField(db_field="description")

    percent_off = DecimalField(db_field="percentOff")      # nullable decimal
    amount_off_dkk = DecimalField(db_field="amountOffDkk") # nullable decimal

    starts_at = DateTimeField(required=True, db_field="startsAt")
    ends_at = DateTimeField(required=True, db_field="endsAt")

    def to_dict(self) -> dict:
        return {
            "id": self.promo_code_id,
            "code": self.code,
            "description": self.description,
            "percent_off": str(self.percent_off) if self.percent_off is not None else None,
            "amount_off_dkk": str(self.amount_off_dkk) if self.amount_off_dkk is not None else None,
            "starts_at": self.starts_at.isoformat() if self.starts_at else None,
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
        }