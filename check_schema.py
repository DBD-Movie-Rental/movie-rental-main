from src.app.repositories.mysql.orm import engine
from sqlalchemy import inspect

insp = inspect(engine)
columns = insp.get_columns("customer")

for col in columns:
    print(
        f"{col['name']:15} {col['type']!s:20} "
        f"nullable={col['nullable']} default={col['default']}"
    )
