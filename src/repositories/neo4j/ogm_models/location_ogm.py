from neomodel import StructuredNode, StringProperty, IntegerProperty


class Location(StructuredNode):
    locationId = IntegerProperty(unique_index=True, required=True)
    address = StringProperty(required=True)
    city = StringProperty(required=True)
