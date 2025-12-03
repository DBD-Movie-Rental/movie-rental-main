from typing import Any, Dict, List, Optional
from src.repositories.mongodb.odm_models.customer_document import Customer, MembershipPlan

class MembershipPlanRepositoryMongo:
    def get_all(self) -> List[Dict[str, Any]]:
        customers = Customer.objects()
        plans = []
        for cust in customers:
            if cust.membership_plan:
                d = cust.membership_plan.to_dict()
                d["customer_id"] = cust.customer_id
                plans.append(d)
        return plans

    def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
        cust = Customer.objects(membership_plan__membership_plan_id=id_).first()
        if not cust or not cust.membership_plan:
            return None
        d = cust.membership_plan.to_dict()
        d["customer_id"] = cust.customer_id
        return d

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = data.get("customer_id")
        if not customer_id:
            raise ValueError("customer_id is required to create a membership plan")
        
        cust = Customer.objects(customer_id=customer_id).first()
        if not cust:
            raise ValueError(f"Customer {customer_id} not found")

        max_id = 0
        all_custs = Customer.objects()
        for c in all_custs:
            if c.membership_plan and c.membership_plan.membership_plan_id > max_id:
                max_id = c.membership_plan.membership_plan_id
        new_id = max_id + 1

        new_plan = MembershipPlan(
            membership_plan_id=new_id,
            membership_type=data.get("membership_type"), # GOLD, SILVER, BRONZE
            starts_on=data.get("starts_on"),
            ends_on=data.get("ends_on"),
            monthly_cost_dkk=data.get("monthly_cost_dkk"),
            membership_id=data.get("membership_id") # This is redundant in Mongo but present in MySQL
        )

        cust.membership_plan = new_plan
        cust.save()
        
        d = new_plan.to_dict()
        d["customer_id"] = cust.customer_id
        return d

    def update(self, id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cust = Customer.objects(membership_plan__membership_plan_id=id_).first()
        if not cust or not cust.membership_plan:
            return None
        
        if "membership_type" in data: cust.membership_plan.membership_type = data["membership_type"]
        if "starts_on" in data: cust.membership_plan.starts_on = data["starts_on"]
        if "ends_on" in data: cust.membership_plan.ends_on = data["ends_on"]
        if "monthly_cost_dkk" in data: cust.membership_plan.monthly_cost_dkk = data["monthly_cost_dkk"]
        if "membership_id" in data: cust.membership_plan.membership_id = data["membership_id"]

        cust.save()
        
        d = cust.membership_plan.to_dict()
        d["customer_id"] = cust.customer_id
        return d

    def delete(self, id_: int) -> bool:
        # Required field, cannot delete.
        return False
