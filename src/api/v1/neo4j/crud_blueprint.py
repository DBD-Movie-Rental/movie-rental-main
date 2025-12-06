from __future__ import annotations

from typing import Callable, Dict, Any

from flask import Blueprint, jsonify, request


def create_crud_blueprint(resource_name: str, repo_factory: Callable[[], Any]) -> Blueprint:
	"""
	Create a CRUD blueprint for Neo4j-backed resources.

	Parameters:
	  - resource_name: base route segment (e.g., "customers")
	  - repo_factory: zero-arg callable returning a repository with
		  methods: get_all(), get_by_id(id), create(data), update(id, data), delete(id)

	Returns:
	  - Flask Blueprint with endpoints:
		GET    /<resource_name>            -> list
		GET    /<resource_name>/<id>       -> get by id
		POST   /<resource_name>            -> create
		PUT    /<resource_name>/<id>       -> update
		DELETE /<resource_name>/<id>       -> delete
	"""

	bp = Blueprint(f"neo4j_{resource_name}", __name__)

	@bp.get(f"/{resource_name}")
	def list_items():
		repo = repo_factory()
		items = repo.get_all()
		return jsonify(items)

	@bp.get(f"/{resource_name}/<int:item_id>")
	def get_item(item_id: int):
		repo = repo_factory()
		item = repo.get_by_id(item_id)
		if not item:
			return jsonify({"error": "not found"}), 404
		return jsonify(item)

	@bp.post(f"/{resource_name}")
	def create_item():
		repo = repo_factory()
		data: Dict[str, Any] = request.get_json(silent=True) or {}
		created = repo.create(data)
		return jsonify(created), 201

	@bp.put(f"/{resource_name}/<int:item_id>")
	def update_item(item_id: int):
		repo = repo_factory()
		data: Dict[str, Any] = request.get_json(silent=True) or {}
		updated = repo.update(item_id, data)
		if not updated:
			return jsonify({"error": "not found"}), 404
		return jsonify(updated)

	@bp.delete(f"/{resource_name}/<int:item_id>")
	def delete_item(item_id: int):
		repo = repo_factory()
		ok = repo.delete(item_id)
		if not ok:
			return jsonify({"error": "not found"}), 404
		return jsonify({"deleted": True})

	return bp


def make_crud_blueprint(resource_name: str, repo: Any, id_converter: str = "int") -> Blueprint:
	"""
	Alternate factory matching existing usage: takes a repo instance and id converter.

	id_converter: "int" or "string" (for routes param type)
	"""
	bp = Blueprint(f"neo4j_{resource_name}", __name__)

	# Choose route parameter converter
	if id_converter == "string":
		param = "<string:item_id>"
		parse = lambda v: v
	else:
		param = "<int:item_id>"
		parse = int

	@bp.get(f"/{resource_name}")
	def list_items():
		items = repo.get_all()
		return jsonify(items)

	@bp.get(f"/{resource_name}/{param}")
	def get_item(item_id):
		item = repo.get_by_id(parse(item_id))
		if not item:
			return jsonify({"error": "not found"}), 404
		return jsonify(item)

	@bp.post(f"/{resource_name}")
	def create_item():
		data: Dict[str, Any] = request.get_json(silent=True) or {}
		created = repo.create(data)
		return jsonify(created), 201

	@bp.put(f"/{resource_name}/{param}")
	def update_item(item_id):
		data: Dict[str, Any] = request.get_json(silent=True) or {}
		updated = repo.update(parse(item_id), data)
		if not updated:
			return jsonify({"error": "not found"}), 404
		return jsonify(updated)

	@bp.delete(f"/{resource_name}/{param}")
	def delete_item(item_id):
		ok = repo.delete(parse(item_id))
		if not ok:
			return jsonify({"error": "not found"}), 404
		return jsonify({"deleted": True})

	return bp

