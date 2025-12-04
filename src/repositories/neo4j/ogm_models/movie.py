from neomodel import StructuredNode, IntegerProperty, StringProperty, FloatProperty, RelationshipTo


class Movie(StructuredNode):
    movieId = IntegerProperty(unique_index=True, required=True)
    title = StringProperty(required=True)
    releaseYear = IntegerProperty(required=True)
    runtimeMin = IntegerProperty(required=True)
    rating = FloatProperty()
    summary = StringProperty()
   
    genres = RelationshipTo('Genre', 'OF_GENRE')
