from flask import Blueprint

from src.repositories.neo4j.customer_repository import CustomerRepository
from .crud_blueprint import make_crud_blueprint

# Parent blueprint for Neo4j routes
bp = Blueprint("neo4j", __name__)

# Register CRUD endpoints for customers
bp.register_blueprint(
	make_crud_blueprint("customers", CustomerRepository(), id_converter="int")
)
