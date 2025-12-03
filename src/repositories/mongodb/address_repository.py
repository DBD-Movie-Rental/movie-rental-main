from typing import Any, Dict, List, Optional
from src.repositories.mongodb.odm_models.customer_document import Customer, Address

class AddressRepositoryMongo:
    def get_all(self) -> List[Dict[str, Any]]:
        customers = Customer.objects()
        addresses = []
        for cust in customers:
            if cust.address:
                # Inject customer_id for parity with MySQL
                addr_dict = cust.address.to_dict()
                addr_dict["customer_id"] = cust.customer_id
                addresses.append(addr_dict)
        return addresses

    def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
        cust = Customer.objects(address__address_id=id_).first()
        if not cust or not cust.address:
            return None
        addr_dict = cust.address.to_dict()
        addr_dict["customer_id"] = cust.customer_id
        return addr_dict

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Requires customer_id
        customer_id = data.get("customer_id")
        if not customer_id:
            raise ValueError("customer_id is required to create an address")
        
        cust = Customer.objects(customer_id=customer_id).first()
        if not cust:
            raise ValueError(f"Customer {customer_id} not found")

        # Generate new ID
        max_id = 0
        all_custs = Customer.objects()
        for c in all_custs:
            if c.address and c.address.address_id > max_id:
                max_id = c.address.address_id
        new_id = max_id + 1

        new_address = Address(
            address_id=new_id,
            address=data.get("address"),
            city=data.get("city"),
            post_code=data.get("post_code")
        )

        # Overwrite existing address
        cust.address = new_address
        cust.save()
        
        addr_dict = new_address.to_dict()
        addr_dict["customer_id"] = cust.customer_id
        return addr_dict

    def update(self, id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cust = Customer.objects(address__address_id=id_).first()
        if not cust or not cust.address:
            return None
        
        if "address" in data: cust.address.address = data["address"]
        if "city" in data: cust.address.city = data["city"]
        if "post_code" in data: cust.address.post_code = data["post_code"]
        
        cust.save()
        
        addr_dict = cust.address.to_dict()
        addr_dict["customer_id"] = cust.customer_id
        return addr_dict

    def delete(self, id_: int) -> bool:
        # Address is required in Customer document, so we cannot delete it.
        return False
