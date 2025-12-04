from neomodel import StructuredNode, IntegerProperty, StringProperty, FloatProperty, DateTimeProperty, RelationshipFrom


class PromoCode(StructuredNode):
    promoCodeId = IntegerProperty(unique_index=True, required=True)
    code = StringProperty(required=True)
    description = StringProperty()
    percentOff = FloatProperty()
    amountOffDkk = FloatProperty()
    startsAt = DateTimeProperty(required=True)
    endsAt = DateTimeProperty(required=True)
    
    rentals = RelationshipFrom('Rental', 'USED_PROMO')
