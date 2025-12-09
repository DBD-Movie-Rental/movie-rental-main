from __future__ import annotations

from typing import Dict, Any, Optional

from .base_repository import Neo4jBaseRepository
from .ogm_models.customer_ogm import Customer


class CustomerRepository(Neo4jBaseRepository[Customer]):
	def __init__(self):
		super().__init__(Customer, id_field="customerId")

