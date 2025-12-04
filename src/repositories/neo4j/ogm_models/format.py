from neomodel import StructuredNode, IntegerProperty, StringProperty

CHOICES = {"DVD", "BLU-RAY", "VHS"}

class Format(StructuredNode):
    formatId = IntegerProperty(unique_index=True, required=True)
    format = StringProperty(required=True, choices=CHOICES)
