from __future__ import annotations

from .base_repository import Neo4jBaseRepository
from .ogm_models.employee_ogm import Employee


class EmployeeRepository(Neo4jBaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee, id_field="employeeId")
