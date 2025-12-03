from typing import Any, Dict, List, Optional
from src.repositories.mongodb.odm_models.location_document import Location, EmployeeEmbedded

class EmployeeRepositoryMongo:
    def get_all(self) -> List[Dict[str, Any]]:
        locations = Location.objects()
        employees = []
        for loc in locations:
            for emp in loc.employees:
                employees.append(emp.to_dict())
        return employees

    def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
        loc = Location.objects(employees__employee_id=id_).first()
        if not loc:
            return None
        for emp in loc.employees:
            if emp.employee_id == id_:
                return emp.to_dict()
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # We need a location_id to insert into.
        # If not provided, we pick the first location found (fallback).
        location_id = data.get("location_id")
        if location_id:
            loc = Location.objects(location_id=location_id).first()
        else:
            loc = Location.objects().first()
        
        if not loc:
            raise ValueError("No location found to add employee to.")

        # Generate ID: max + 1
        max_id = 0
        all_locs = Location.objects()
        for l in all_locs:
            for e in l.employees:
                if e.employee_id > max_id:
                    max_id = e.employee_id
        new_id = max_id + 1

        new_emp = EmployeeEmbedded(
            employee_id=new_id,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone_number=data.get("phone_number"),
            email=data.get("email"),
            is_active=data.get("is_active", True)
        )

        loc.employees.append(new_emp)
        loc.save()
        return new_emp.to_dict()

    def update(self, id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loc = Location.objects(employees__employee_id=id_).first()
        if not loc:
            return None
        
        target_emp = None
        for emp in loc.employees:
            if emp.employee_id == id_:
                target_emp = emp
                break
        
        if not target_emp:
            return None

        if "first_name" in data: target_emp.first_name = data["first_name"]
        if "last_name" in data: target_emp.last_name = data["last_name"]
        if "phone_number" in data: target_emp.phone_number = data["phone_number"]
        if "email" in data: target_emp.email = data["email"]
        if "is_active" in data: target_emp.is_active = data["is_active"]

        loc.save()
        return target_emp.to_dict()

    def delete(self, id_: int) -> bool:
        loc = Location.objects(employees__employee_id=id_).first()
        if not loc:
            return False
        
        original_len = len(loc.employees)
        loc.employees = [e for e in loc.employees if e.employee_id != id_]
        
        if len(loc.employees) < original_len:
            loc.save()
            return True
        return False
