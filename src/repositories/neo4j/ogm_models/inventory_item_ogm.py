from neomodel import StructuredNode, IntegerProperty, RelationshipTo, BooleanProperty, RelationshipFrom
from .location_ogm import Location
from .movie_ogm import Movie
from .format_ogm import Format


class InventoryItem(StructuredNode):
    inventoryItemId = IntegerProperty(unique_index=True, required=True)
    status = BooleanProperty(default=True)
    
    location = RelationshipTo(Location, 'LOCATED_AT')
    movie = RelationshipTo(Movie, 'IS_COPY_OF')
    format = RelationshipTo(Format, 'HAS_FORMAT')
    # Use fully qualified string target to avoid circular import and ensure resolution
    rentals = RelationshipFrom('src.repositories.neo4j.ogm_models.rental_ogm.Rental', 'HAS_ITEM')
