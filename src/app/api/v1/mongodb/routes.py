from flask import Blueprint, jsonify, request
from src.app.repositories.mongodb.repository import CustomerRepository

bp = Blueprint("mongodb_routes", __name__)
repo = CustomerRepository()

@bp.get("/customers")
def get_customers():
    customers = repo.get_all_customers()
    return jsonify([c.to_dict() for c in customers])


