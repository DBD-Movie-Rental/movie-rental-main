from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from .base import Base
import enum

class ApiUserRole(enum.Enum):
    ADMIN = 'ADMIN'
    SUPERUSER = 'SUPERUSER'
    USER = 'USER'

class ApiUser(Base):
    __tablename__ = 'api_user'

    api_user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(ApiUserRole), nullable=False, default=ApiUserRole.USER)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.api_user_id,
            'username': self.username,
            'role': self.role.value if self.role else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
