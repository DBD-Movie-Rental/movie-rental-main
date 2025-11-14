from flask import Blueprint, jsonify, request
from src.repositories.mongodb.customer_repository import CustomerRepositoryMongo

bp = Blueprint("mongodb_routes", __name__)
repo = CustomerRepositoryMongo()

@bp.get("/customers")
def get_customers():
    customers = repo.get_all_customers()
    return jsonify(customers)

@bp.post("/customers")
def create_customer():
    data = request.get_json()
    # Basic validation (can be improved later)
    required = ["customer_id", "first_name", "last_name", "email"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    new_id = repo.create_customer(data)
    return jsonify({"customer_id": new_id}), 201
