from flask import Blueprint, jsonify, request
from src.repositories.mysql.customer_repository import CustomerRepository
from src.repositories.mysql.genre_repository import GenreRepository
from src.repositories.mysql.movie_repository import MovieRepository
from src.repositories.mysql.employee_repository import EmployeeRepository
from src.repositories.mysql.address_repository import AddressRepository
from src.repositories.mysql.fee_repository import FeeRepository
from src.repositories.mysql.format_repository import FormatRepository
from src.repositories.mysql.location_repository import LocationRepository
from src.repositories.mysql.inventory_item_repository import InventoryItemRepository
from src.repositories.mysql.membership_repository import MembershipRepository
from src.repositories.mysql.membership_plan_repository import MembershipPlanRepository
from src.repositories.mysql.promo_code_repository import PromoCodeRepository
from src.repositories.mysql.rental_repository import RentalRepository
from src.repositories.mysql.payment_repository import PaymentRepository
from src.repositories.mysql.review_repository import ReviewRepository
from .crud_blueprint import make_crud_blueprint

bp = Blueprint("mysql_routes", __name__)
repo = CustomerRepository()
genre_repo = GenreRepository()
movie_repo = MovieRepository()
employee_repo = EmployeeRepository()
address_repo = AddressRepository()
fee_repo = FeeRepository()
format_repo = FormatRepository()
location_repo = LocationRepository()
inventory_item_repo = InventoryItemRepository()
membership_repo = MembershipRepository()
membership_plan_repo = MembershipPlanRepository()
promo_code_repo = PromoCodeRepository()
rental_repo = RentalRepository()
payment_repo = PaymentRepository()
review_repo = ReviewRepository()

# Register generic CRUD routes for customers using the CustomerRepository
customers_bp = make_crud_blueprint("customers", repo, id_converter="int")
bp.register_blueprint(customers_bp)

# Register generic CRUD routes for genres (example of BaseRepository usage)
genres_bp = make_crud_blueprint("genres", genre_repo, id_converter="int")
bp.register_blueprint(genres_bp)

# Register generic CRUD routes for movies
movies_bp = make_crud_blueprint("movies", movie_repo, id_converter="int")
bp.register_blueprint(movies_bp)

# Register generic CRUD routes for employees
employees_bp = make_crud_blueprint("employees", employee_repo, id_converter="int")
bp.register_blueprint(employees_bp)

# Register generic CRUD routes for addresses
addresses_bp = make_crud_blueprint("addresses", address_repo, id_converter="int")
bp.register_blueprint(addresses_bp)

# Register generic CRUD routes for fees
fees_bp = make_crud_blueprint("fees", fee_repo, id_converter="int")
bp.register_blueprint(fees_bp)

# Register generic CRUD routes for formats
formats_bp = make_crud_blueprint("formats", format_repo, id_converter="int")
bp.register_blueprint(formats_bp)

# Register generic CRUD routes for locations
locations_bp = make_crud_blueprint("locations", location_repo, id_converter="int")
bp.register_blueprint(locations_bp)

# Register generic CRUD routes for inventory_items
inventory_items_bp = make_crud_blueprint("inventory_items", inventory_item_repo, id_converter="int")
bp.register_blueprint(inventory_items_bp)

# Register generic CRUD routes for memberships
memberships_bp = make_crud_blueprint("memberships", membership_repo, id_converter="int")
bp.register_blueprint(memberships_bp)

# Register generic CRUD routes for membership_plans
membership_plans_bp = make_crud_blueprint("membership_plans", membership_plan_repo, id_converter="int")
bp.register_blueprint(membership_plans_bp)

# Register generic CRUD routes for promo_codes
promo_codes_bp = make_crud_blueprint("promo_codes", promo_code_repo, id_converter="int")
bp.register_blueprint(promo_codes_bp)

# Register generic CRUD routes for rentals
rentals_bp = make_crud_blueprint("rentals", rental_repo, id_converter="int")
bp.register_blueprint(rentals_bp)

# Register generic CRUD routes for payments
payments_bp = make_crud_blueprint("payments", payment_repo, id_converter="int")
bp.register_blueprint(payments_bp)

# Register generic CRUD routes for reviews
reviews_bp = make_crud_blueprint("reviews", review_repo, id_converter="int")
bp.register_blueprint(reviews_bp)
