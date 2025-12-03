from flask import Blueprint

from .crud_blueprint import make_crud_blueprint  # the Mongo-specific one

from src.repositories.mongodb.customer_repository import CustomerRepositoryMongo
from src.repositories.mongodb.movie_repository import MovieRepositoryMongo
from src.repositories.mongodb.location_repository import LocationRepositoryMongo
from src.repositories.mongodb.rental_repository import RentalRepositoryMongo
from src.repositories.mongodb.genre_repository import GenreRepositoryMongo
from src.repositories.mongodb.format_repository import FormatRepositoryMongo
from src.repositories.mongodb.promo_code_repository import PromoCodeRepositoryMongo
from src.repositories.mongodb.membership_type_repository import MembershipTypeRepositoryMongo
from src.repositories.mongodb.fee_type_repository import FeeTypeRepositoryMongo
from src.repositories.mongodb.employee_repository import EmployeeRepositoryMongo
from src.repositories.mongodb.address_repository import AddressRepositoryMongo
from src.repositories.mongodb.inventory_item_repository import InventoryItemRepositoryMongo
from src.repositories.mongodb.payment_repository import PaymentRepositoryMongo
from src.repositories.mongodb.review_repository import ReviewRepositoryMongo
from src.repositories.mongodb.membership_plan_repository import MembershipPlanRepositoryMongo

# Blueprint for MongoDB routes
bp = Blueprint("mongodb_routes", __name__)

# Initialize repositories
customer_repo = CustomerRepositoryMongo()
movie_repo = MovieRepositoryMongo()
location_repo = LocationRepositoryMongo()
rental_repo = RentalRepositoryMongo()
genre_repo = GenreRepositoryMongo()
format_repo = FormatRepositoryMongo()
promo_code_repo = PromoCodeRepositoryMongo()
membership_type_repo = MembershipTypeRepositoryMongo()
fee_type_repo = FeeTypeRepositoryMongo()
employee_repo = EmployeeRepositoryMongo()
address_repo = AddressRepositoryMongo()
inventory_item_repo = InventoryItemRepositoryMongo()
payment_repo = PaymentRepositoryMongo()
review_repo = ReviewRepositoryMongo()
membership_plan_repo = MembershipPlanRepositoryMongo()

# Register CRUD blueprints for each resource
bp.register_blueprint(make_crud_blueprint("customers", customer_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("movies", movie_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("locations", location_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("rentals", rental_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("genres", genre_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("formats", format_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("promo_codes", promo_code_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("memberships", membership_type_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("fees", fee_type_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("employees", employee_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("addresses", address_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("inventory_items", inventory_item_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("payments", payment_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("reviews", review_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("membership_plans", membership_plan_repo, id_converter="int"))
