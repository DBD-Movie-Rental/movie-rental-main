from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

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

# ---------------------------------------------------------
# Custom Rental Routes (Transactional)
# ---------------------------------------------------------
rentals_bp = Blueprint("mongodb_rentals", __name__)

@rentals_bp.get("/rentals")
def list_rentals():
    try:
        items = rental_repo.get_all()
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rentals_bp.get("/rentals/detailed")
def list_rentals_detailed():
    try:
        items = rental_repo.get_all_details()
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rentals_bp.get("/rentals/<int:item_id>")
def get_rental(item_id):
    try:
        item = rental_repo.get_by_id(item_id)
        if not item:
            return jsonify({"error": "Not found"}), 404
        return jsonify(item), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rentals_bp.get("/rentals/<int:item_id>/detailed")
def get_rental_details(item_id):
    try:
        item = rental_repo.get_details(item_id)
        if not item:
            return jsonify({"error": "Not found"}), 404
        return jsonify(item), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rentals_bp.post("/rentals")
@jwt_required()
def create_rental():
    """
    Transactional Rental Creation
    """
    try:
        data = request.get_json() or {}
        # Extract required fields for the transactional method
        customer_id = data.get("customer_id")
        employee_id = data.get("employee_id")
        promo_code_id = data.get("promo_code_id")
        inventory_items = data.get("inventory_items", [])

        if not customer_id or not inventory_items:
             return jsonify({"error": "Missing required fields: customer_id, inventory_items"}), 400

        created = rental_repo.create_rental(
            customer_id=customer_id,
            employee_id=employee_id,
            promo_code_id=promo_code_id,
            inventory_items=inventory_items
        )
        return jsonify(created), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rentals_bp.post("/rentals/reservation")
@jwt_required()
def create_reservation():
    """
    Transactional Reservation Creation
    """
    try:
        data = request.get_json() or {}
        customer_id = data.get("customer_id")
        employee_id = data.get("employee_id")
        promo_code_id = data.get("promo_code_id")
        inventory_items = data.get("inventory_items", [])

        if not customer_id or not inventory_items:
             return jsonify({"error": "Missing required fields: customer_id, inventory_items"}), 400

        created = rental_repo.create_reservation(
            customer_id=customer_id,
            employee_id=employee_id,
            promo_code_id=promo_code_id,
            inventory_items=inventory_items
        )
        return jsonify(created), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rentals_bp.put("/rentals/<int:item_id>")
@jwt_required()
def update_rental(item_id):
    try:
        data = request.get_json() or {}
        updated = rental_repo.update(item_id, data)
        if not updated:
            return jsonify({"error": "Not found"}), 404
        return jsonify(updated), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rentals_bp.delete("/rentals/<int:item_id>")
@jwt_required()
def delete_rental(item_id):
    try:
        ok = rental_repo.delete(item_id)
        if not ok:
            return jsonify({"error": "Not found"}), 404
        return ("", 204)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register the custom rentals blueprint
bp.register_blueprint(rentals_bp)


# Register CRUD blueprints for each resource
bp.register_blueprint(make_crud_blueprint("customers", customer_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("movies", movie_repo, id_converter="int"))
bp.register_blueprint(make_crud_blueprint("locations", location_repo, id_converter="int"))
# bp.register_blueprint(make_crud_blueprint("rentals", rental_repo, id_converter="int")) # Replaced by custom blueprint
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

