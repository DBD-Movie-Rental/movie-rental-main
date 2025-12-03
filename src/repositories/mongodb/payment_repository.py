from typing import Any, Dict, List, Optional
from datetime import datetime
from src.repositories.mongodb.odm_models.rental_document import Rental, PaymentEmbedded

class PaymentRepositoryMongo:
    def get_all(self) -> List[Dict[str, Any]]:
        rentals = Rental.objects()
        payments = []
        for r in rentals:
            for p in r.payments:
                d = p.to_dict()
                d["rental_id"] = r.rental_id
                payments.append(d)
        return payments

    def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
        r = Rental.objects(payments__payment_id=id_).first()
        if not r:
            return None
        for p in r.payments:
            if p.payment_id == id_:
                d = p.to_dict()
                d["rental_id"] = r.rental_id
                return d
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        rental_id = data.get("rental_id")
        if not rental_id:
            raise ValueError("rental_id is required to create a payment")
        
        r = Rental.objects(rental_id=rental_id).first()
        if not r:
            raise ValueError(f"Rental {rental_id} not found")

        max_id = 0
        all_rentals = Rental.objects()
        for rent in all_rentals:
            for p in rent.payments:
                if p.payment_id > max_id:
                    max_id = p.payment_id
        new_id = max_id + 1

        new_payment = PaymentEmbedded(
            payment_id=new_id,
            amount_dkk=data.get("amount_dkk"),
            created_at=datetime.utcnow()
        )
        
        r.payments.append(new_payment)
        r.save()
        
        d = new_payment.to_dict()
        d["rental_id"] = r.rental_id
        return d

    def update(self, id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        r = Rental.objects(payments__payment_id=id_).first()
        if not r:
            return None
        
        target_p = None
        for p in r.payments:
            if p.payment_id == id_:
                target_p = p
                break
        
        if not target_p:
            return None

        if "amount_dkk" in data: target_p.amount_dkk = data["amount_dkk"]

        r.save()
        
        d = target_p.to_dict()
        d["rental_id"] = r.rental_id
        return d

    def delete(self, id_: int) -> bool:
        r = Rental.objects(payments__payment_id=id_).first()
        if not r:
            return False
        
        original_len = len(r.payments)
        r.payments = [p for p in r.payments if p.payment_id != id_]
        
        if len(r.payments) < original_len:
            r.save()
            return True
        return False
