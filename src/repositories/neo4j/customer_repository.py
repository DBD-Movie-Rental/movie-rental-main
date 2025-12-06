from __future__ import annotations

from typing import Dict, Any, Optional

from .base_repository import Neo4jBaseRepository
from .ogm_models.customer_ogm import Customer


class CustomerRepository(Neo4jBaseRepository[Customer]):
	def __init__(self):
		# customer OGM uses property name "customerId" for lookup
		super().__init__(Customer, id_field="customerId")

	# Example of a custom finder beyond the base helpers
	def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
		node = Customer.nodes.first(email=email)
		return self._to_dict(node) if node else None

