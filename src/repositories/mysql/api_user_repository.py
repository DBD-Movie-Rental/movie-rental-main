from typing import Optional, Dict, Any
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from .base_repository import BaseRepository
from .orm_models.api_user_orm import ApiUser, ApiUserRole
from src.security.passwords import hash_password

class ApiUserRepository(BaseRepository[ApiUser]):
    def __init__(self, session_factory: sessionmaker | None = None):
        if session_factory is not None:
            super().__init__(ApiUser, session_factory=session_factory)
        else:
            # use default SessionLocal from BaseRepository
            super().__init__(ApiUser)

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._SessionLocal() as session:
            stmt = select(ApiUser).where(ApiUser.username == username)
            obj = session.execute(stmt).scalar_one_or_none()
            return self._to_dict(obj) if obj else None

    def create_user(self, username: str, password: str, role: ApiUserRole = ApiUserRole.USER) -> Dict[str, Any]:
        with self._SessionLocal() as session:
            existing = session.execute(select(ApiUser).where(ApiUser.username == username)).scalar_one_or_none()
            if existing:
                raise ValueError('Username already exists')
            pw_hash = hash_password(password)
            user = ApiUser(username=username, password_hash=pw_hash, role=role)
            session.add(user)
            session.commit()
            session.refresh(user)
            return self._to_dict(user)

    # override _to_dict to exclude password_hash
    def _to_dict(self, obj: Any) -> Dict[str, Any]:  # type: ignore[override]
        if obj is None:
            return {}
        return {
            'id': obj.api_user_id,
            'username': obj.username,
            'role': obj.role.value if obj.role else None,
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }
