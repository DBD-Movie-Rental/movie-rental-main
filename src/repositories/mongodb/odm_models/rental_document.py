from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    StringField,
    DateTimeField,
    Decimal128Field as DecimalField,
)


class RentalItemEmbedded(EmbeddedDocument):
    rental_item_id = IntField(required=True, db_field="rentalItemId")
    inventory_item_id = IntField(required=True, db_field="inventoryItemId")
    movie_id = IntField(required=True, db_field="movieId")
    format_id = IntField(required=True, db_field="formatId")


class PaymentEmbedded(EmbeddedDocument):
    payment_id = IntField(required=True, db_field="paymentId")
    amount_dkk = DecimalField(required=True, db_field="amountDkk")
    created_at = DateTimeField(required=True, db_field="createdAt")

    def to_dict(self) -> dict:
        return {
            "id": self.payment_id,
            "amount_dkk": float(self.amount_dkk) if self.amount_dkk is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FeeSnapshotEmbedded(EmbeddedDocument):
    fee_type = StringField(db_field="feeType")
    default_amount_dkk = DecimalField(db_field="defaultAmountDkk")


class RentalFeeEmbedded(EmbeddedDocument):
    rental_fee_id = IntField(required=True, db_field="rentalFeeId")
    fee_id = IntField(required=True, db_field="feeId")
    amount_dkk = DecimalField(required=True, db_field="amountDkk")
    snapshot = EmbeddedDocumentField(FeeSnapshotEmbedded, db_field="snapshot")


class PromoSnapshotEmbedded(EmbeddedDocument):
    promo_code_id = IntField(db_field="promoCodeId")
    code = StringField(db_field="code")
    percent_off = DecimalField(db_field="percentOff")
    amount_off_dkk = DecimalField(db_field="amountOffDkk")
    starts_at = DateTimeField(db_field="startsAt")
    ends_at = DateTimeField(db_field="endsAt")


class Rental(Document):
    meta = {
        "collection": "rentals",
        "auto_create_index": False,
    }

    rental_id = IntField(required=True, unique=True, db_field="rentalId")
    customer_id = IntField(required=True, db_field="customerId")
    location_id = IntField(required=True, db_field="locationId")
    employee_id = IntField(db_field="employeeId")

    status = StringField(
        required=True,
        choices=("RESERVED", "OPEN", "RETURNED", "LATE", "CANCELLED"),
        db_field="status",
    )

    rented_at = DateTimeField(db_field="rentedAtDatetime")
    returned_at = DateTimeField(db_field="returnedAtDatetime")
    due_at = DateTimeField(db_field="dueAtDatetime")
    reserved_at = DateTimeField(db_field="reservedAtDatetime")

    items = EmbeddedDocumentListField(RentalItemEmbedded, db_field="items")
    payments = EmbeddedDocumentListField(PaymentEmbedded, db_field="payments")
    fees = EmbeddedDocumentListField(RentalFeeEmbedded, db_field="fees")
    promo = EmbeddedDocumentField(PromoSnapshotEmbedded, db_field="promo")

    def to_dict(self) -> dict:
        return {
            "id": self.rental_id,
            "customer_id": self.customer_id,
            "location_id": self.location_id,
            "employee_id": self.employee_id,
            "status": self.status,
            "rented_at": self.rented_at.isoformat() if self.rented_at else None,
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "reserved_at": self.reserved_at.isoformat() if self.reserved_at else None,
        }
    
    def to_detailed_dict(self) -> dict:
        payload = self.to_dict()
        payload["items"] = [
            {
                "rental_item_id": item.rental_item_id,
                "inventory_item_id": item.inventory_item_id,
                "movie_id": item.movie_id,
                "format_id": item.format_id,
            }
            for item in self.items
        ]
        
        payload["payments"] = [
            {
                "payment_id": payment.payment_id,
                "amount_dkk": float(payment.amount_dkk),
                "created_at": payment.created_at.isoformat()
                if payment.created_at
                else None,
            }
            for payment in self.payments
        ]

        payload["fees"] = [
            {
                "rental_fee_id": fee.rental_fee_id,
                "fee_id": fee.fee_id,
                "amount_dkk": float(fee.amount_dkk),
                "snapshot": {
                    "fee_type": fee.snapshot.fee_type,
                    "default_amount_dkk": float(fee.snapshot.default_amount_dkk),
                }
                if fee.snapshot
                else None,
            }
            for fee in self.fees
        ]

        if self.promo:
            payload["promo"] = {
                "promo_code_id": self.promo.promo_code_id,
                "code": self.promo.code,
                "percent_off": float(self.promo.percent_off)
                if self.promo.percent_off
                else None,
                "amount_off_dkk": float(self.promo.amount_off_dkk)
                if self.promo.amount_off_dkk
                else None,
                "starts_at": self.promo.starts_at.isoformat()
                if self.promo.starts_at
                else None,
                "ends_at": self.promo.ends_at.isoformat()
                if self.promo.ends_at
                else None,
            }
        else:
            payload["promo"] = None
        return payload