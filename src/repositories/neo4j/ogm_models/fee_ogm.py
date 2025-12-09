from neomodel import StructuredNode, IntegerProperty, FloatProperty, StringProperty, RelationshipFrom


FEE_TYPES = (
    ("LATE", "LATE"),
    ("DAMAGED", "DAMAGED"),
    ("OTHER", "OTHER"),
)


class Fee(StructuredNode):
    feeId = IntegerProperty(unique_index=True, required=True)
    feeType = StringProperty(required=True, choices=FEE_TYPES)
    amountDkk = FloatProperty(required=True)
    
    # Use fully qualified string target to avoid circular import and ensure resolution
    rental = RelationshipFrom('src.repositories.neo4j.ogm_models.rental_ogm.Rental', 'HAS_FEE')
