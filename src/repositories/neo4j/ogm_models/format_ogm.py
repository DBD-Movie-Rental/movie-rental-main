from neomodel import StructuredNode, IntegerProperty, StringProperty

CHOICES = (
    ("DVD", "DVD"),
    ("BLU-RAY", "BLU-RAY"),
    ("VHS", "VHS"),
)

class Format(StructuredNode):
    formatId = IntegerProperty(unique_index=True, required=True)
    format = StringProperty(required=True, choices=CHOICES)
