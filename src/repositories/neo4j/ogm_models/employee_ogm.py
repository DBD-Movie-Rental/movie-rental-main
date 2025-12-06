from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, RelationshipTo


class Employee(StructuredNode):
    employeeId = IntegerProperty(unique_index=True, required=True)
    firstName = StringProperty(required=True)
    lastName = StringProperty(required=True)
    phoneNumber = StringProperty(required=True)
    email = StringProperty(required=True)
    isActive = BooleanProperty(default=True)
    
    location = RelationshipTo('Location', 'EMPLOYED_AT')
