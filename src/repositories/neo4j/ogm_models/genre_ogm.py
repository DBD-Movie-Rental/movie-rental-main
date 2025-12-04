from neomodel import StructuredNode, IntegerProperty, StringProperty


class Genre(StructuredNode):
    genreId = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
