from flask import Blueprint, jsonify, request


def make_crud_blueprint(resource_name: str, repo, id_converter: str = "int") -> Blueprint:
    """Create a CRUD blueprint for a resource using a repository.

    repo must implement: get_all(), get_by_id(id), create(data), update(id, data), delete(id)
    resource_name: e.g., "genres" -> routes like /genres, /genres/<id>
    id_converter: Flask converter type, default "int".
    """

    bp = Blueprint(f"mysql_{resource_name}", __name__)

    @bp.get(f"/{resource_name}")
    def list_resources():
        try:
            items = repo.get_all()
            return jsonify(items), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @bp.get(f"/{resource_name}/<{id_converter}:item_id>")
    def get_resource(item_id):  # type: ignore[no-redef]
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return jsonify({"error": "Not found"}), 404
            return jsonify(item), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @bp.post(f"/{resource_name}")
    def create_resource():
        try:
            data = request.get_json() or {}
            created = repo.create(data)
            return jsonify(created), 201
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @bp.put(f"/{resource_name}/<{id_converter}:item_id>")
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

    @bp.delete(f"/{resource_name}/<{id_converter}:item_id>")
    def delete_resource(item_id):  # type: ignore[no-redef]
        try:
            ok = repo.delete(item_id)
            if not ok:
                return jsonify({"error": "Not found"}), 404
            return ("", 204)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return bp
