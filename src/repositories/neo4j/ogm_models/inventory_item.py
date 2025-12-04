from neomodel import StructuredNode, IntegerProperty, RelationshipTo, BooleanProperty, RelationshipFrom



class InventoryItem(StructuredNode):
    inventoryItemId = IntegerProperty(unique_index=True, required=True)
    status = BooleanProperty(required=True, default=True)
    
    location = RelationshipTo('Location', 'LOCATED_AT')
    movie = RelationshipTo('Movie', 'IS_COPY_OF')
    format = RelationshipTo('Format', 'HAS_FORMAT')
    rentals = RelationshipFrom('Rental', 'HAS_ITEM')
