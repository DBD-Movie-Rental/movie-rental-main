from .base_repository import BaseRepository
from .orm_models.employee_orm import Employee


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)
