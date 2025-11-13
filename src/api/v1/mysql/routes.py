from flask import Blueprint, jsonify, request
from src.repositories.mysql.customer_repository import CustomerRepository

bp = Blueprint("mysql_routes", __name__)
repo = CustomerRepository()

@bp.get("/customers")
def get_customers():
    customers = repo.get_all_customers()
    return jsonify([c.to_dict() for c in customers])

@bp.post("/customers")
def create_customer():
    data = request.get_json()

    required_fields = [
        "first_name", "last_name", "email", "phone_number",
        "address", "city", "post_code"
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        new_id = repo.create_customer_via_proc(data)
        if new_id:
            return jsonify({"status": "created", "new_customer_id": new_id}), 201
        else:
            return jsonify({"status": "created_but_id_unknown"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.delete("/customers/<int:customer_id>")
def delete_customer(customer_id: int):
    try:
        deleted = repo.delete_customer(customer_id)
        if deleted:
            return jsonify({"status": "deleted", "customer_id": customer_id}), 200
        else:
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
