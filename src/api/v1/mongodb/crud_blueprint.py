# src/api/v1/mongodb/crud_blueprint.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required


def make_crud_blueprint(resource_name: str, repo, id_converter: str = "int") -> Blueprint:
    """CRUD blueprint for MongoDB resources.

    repo must implement: get_all(), get_by_id(id), create(data), update(id, data), delete(id)
    Optionally, repo can implement: get_details(id) for /<resource>/<id>/details
    """

    bp = Blueprint(f"mongodb_{resource_name}", __name__)

    # GET /<resource>
    @bp.get(f"/{resource_name}")
    def list_resources():
        try:
            items = repo.get_all()
            return jsonify(items), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    # GET /<resource>/detailed
    @bp.get(f"/{resource_name}/detailed")
    def list_resources_detailed():
        try:
            if not hasattr(repo, "get_all_details"):
                return jsonify(
                    {"error": "Detailed list not supported for this resource"}
                ), 400

            items = repo.get_all_details()
            return jsonify(items), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # GET /<resource>/<id>
    @bp.get(f"/{resource_name}/<{id_converter}:item_id>")
    def get_resource(item_id):  # type: ignore[no-redef]
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return jsonify({"error": "Not found"}), 404
            return jsonify(item), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    # GET /<resource>/<id>/detailed
    @bp.get(f"/{resource_name}/<{id_converter}:item_id>/detailed")
    def get_resource_details(item_id):  # type: ignore[no-redef]
        try:
            if not hasattr(repo, "get_details"):
                return jsonify(
                    {"error": "Detailed view not supported for this resource"}
                ), 400

            item = repo.get_details(item_id)
            if not item:
                return jsonify({"error": "Not found"}), 404

            return jsonify(item), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # POST /<resource>
    @bp.post(f"/{resource_name}")
    @jwt_required()
    def create_resource():
        try:
            data = request.get_json() or {}
            created = repo.create(data)
            return jsonify(created), 201
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # PUT /<resource>/<id>
    @bp.put(f"/{resource_name}/<{id_converter}:item_id>")
    @jwt_required()
    def update_resource(item_id):  # type: ignore[no-redef]
        try:
            data = request.get_json() or {}
            updated = repo.update(item_id, data)
            if not updated:
                return jsonify({"error": "Not found"}), 404
            return jsonify(updated), 200
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # DELETE /<resource>/<id>
    @bp.delete(f"/{resource_name}/<{id_converter}:item_id>")
    @jwt_required()
    def delete_resource(item_id):  # type: ignore[no-redef]
        try:
            ok = repo.delete(item_id)
            if not ok:
                return jsonify({"error": "Not found"}), 404
            return ("", 204)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return bp