from flask import Blueprint, jsonify

bp = Blueprint("mongodb_health", __name__)

@bp.get("/health")
def health():
    return jsonify({"backend": "mongodb", "status": "ok"})
