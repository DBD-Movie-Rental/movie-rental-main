from typing import Any, Dict, List, Optional
from src.repositories.mongodb.odm_models.location_document import Location, InventoryItemEmbedded

class InventoryItemRepositoryMongo:
    def get_all(self) -> List[Dict[str, Any]]:
        locations = Location.objects()
        items = []
        for loc in locations:
            for item in loc.inventory:
                d = item.to_dict()
                d["location_id"] = loc.location_id
                items.append(d)
        return items

    def get_by_id(self, id_: int) -> Optional[Dict[str, Any]]:
        loc = Location.objects(inventory__inventory_item_id=id_).first()
        if not loc:
            return None
        for item in loc.inventory:
            if item.inventory_item_id == id_:
                d = item.to_dict()
                d["location_id"] = loc.location_id
                return d
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        location_id = data.get("location_id")
        if location_id:
            loc = Location.objects(location_id=location_id).first()
        else:
            loc = Location.objects().first()
        
        if not loc:
            raise ValueError("No location found to add inventory item to.")

        max_id = 0
        all_locs = Location.objects()
        for l in all_locs:
            for i in l.inventory:
                if i.inventory_item_id > max_id:
                    max_id = i.inventory_item_id
        new_id = max_id + 1

        # Handle status conversion if necessary. 
        # MySQL uses int (1=available), Mongo uses String in ODM.
        status_val = data.get("status", "1")
        
        new_item = InventoryItemEmbedded(
            inventory_item_id=new_id,
            movie_id=data.get("movie_id"),
            format_id=data.get("format_id"),
            status=str(status_val)
        )
        
        loc.inventory.append(new_item)
        loc.save()
        
        d = new_item.to_dict()
        d["location_id"] = loc.location_id
        return d

    def update(self, id_: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loc = Location.objects(inventory__inventory_item_id=id_).first()
        if not loc:
            return None
        
        target_item = None
        for item in loc.inventory:
            if item.inventory_item_id == id_:
                target_item = item
                break
        
        if not target_item:
            return None

        if "movie_id" in data: target_item.movie_id = data["movie_id"]
        if "format_id" in data: target_item.format_id = data["format_id"]
        if "status" in data: target_item.status = str(data["status"])

        loc.save()
        
        d = target_item.to_dict()
        d["location_id"] = loc.location_id
        return d

    def delete(self, id_: int) -> bool:
        loc = Location.objects(inventory__inventory_item_id=id_).first()
        if not loc:
            return False
        
        original_len = len(loc.inventory)
        loc.inventory = [i for i in loc.inventory if i.inventory_item_id != id_]
        
        if len(loc.inventory) < original_len:
            loc.save()
            return True
        return False
