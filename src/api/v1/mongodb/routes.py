from flask import Blueprint, jsonify, request
from src.repositories.mongodb.customer_repository import CustomerRepositoryMongo

bp = Blueprint("mongodb_routes", __name__)
repo = CustomerRepositoryMongo()


@bp.get("/customers")
def get_customers():
    try:
        customers = repo.get_all_customers()
        return jsonify(customers), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch customers", "details": str(e)}), 500


@bp.get("/customers/<int:customer_id>")
def get_customer(customer_id: int):
    try:
        customer = repo.get_customer(customer_id)
        if customer is None:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch customer", "details": str(e)}), 500


# Customer id releys on auto-generated MySQL ID, so creation is not supported here
# TODO: Implement a workaround if needed - maybe UUIDs?
@bp.post("/customers")
def create_customer():
    return jsonify({"error": "Creating customers is not supported in MongoDB repository"}), 501