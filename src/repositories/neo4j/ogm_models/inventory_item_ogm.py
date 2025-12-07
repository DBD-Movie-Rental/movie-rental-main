from neomodel import StructuredNode, IntegerProperty, RelationshipTo, BooleanProperty, RelationshipFrom
from .location_ogm import Location
from .movie_ogm import Movie
from .format_ogm import Format
from .rental_ogm import Rental


class InventoryItem(StructuredNode):
    inventoryItemId = IntegerProperty(unique_index=True, required=True)
    status = BooleanProperty(default=True)
    
    location = RelationshipTo(Location, 'LOCATED_AT')
    movie = RelationshipTo(Movie, 'IS_COPY_OF')
    format = RelationshipTo(Format, 'HAS_FORMAT')
    rentals = RelationshipFrom(Rental, 'HAS_ITEM')
