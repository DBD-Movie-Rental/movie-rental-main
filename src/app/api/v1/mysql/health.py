from flask import Blueprint, jsonify

bp = Blueprint("mysql_health", __name__)

@bp.get("/health")
def health():
    return jsonify({"backend": "mysql", "status": "ok"})
