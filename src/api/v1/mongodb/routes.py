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

# Register CRUD blueprints for each resource
bp.register_blueprint(make_crud_blueprint("customers", customer_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("movies", movie_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("locations", location_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("rentals", rental_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("genres", genre_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("formats", format_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("promo_codes", promo_code_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("membership_types", membership_type_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("fee_types", fee_type_repo, id_converter="int"))
