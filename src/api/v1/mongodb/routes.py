# src/api/v1/mongodb/routes.py
from flask import Blueprint, jsonify

from src.repositories.mongodb.customer_repository import CustomerRepositoryMongo
from src.api.v1.mysql.crud_blueprint import make_crud_blueprint  # or move to a shared module

bp = Blueprint("mongodb_routes", __name__)

customer_repo = CustomerRepositoryMongo()

# /api/v1/mongodb/customers, /api/v1/mongodb/customers/<int:item_id>, etc.
customers_bp = make_crud_blueprint("customers", customer_repo, id_converter="int")
bp.register_blueprint(customers_bp)


@bp.get("/health")
def health():
    try:
        CustomerRepositoryMongo().get_all()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500
