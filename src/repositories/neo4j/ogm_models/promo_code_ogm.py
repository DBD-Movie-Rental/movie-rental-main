from neomodel import StructuredNode, IntegerProperty, StringProperty, FloatProperty, DateTimeProperty, RelationshipFrom


class PromoCode(StructuredNode):
    promoCodeId = IntegerProperty(unique_index=True, required=True)
    code = StringProperty(required=True)
    description = StringProperty()
    percentOff = FloatProperty()
    amountOffDkk = FloatProperty()
    startsAt = DateTimeProperty(required=True)
    endsAt = DateTimeProperty(required=True)
    
    # Use fully qualified string target to avoid circular import and ensure resolution
    rentals = RelationshipFrom('src.repositories.neo4j.ogm_models.rental_ogm.Rental', 'USED_PROMO')
