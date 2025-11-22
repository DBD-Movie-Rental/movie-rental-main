from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
from src.repositories.mysql.api_user_repository import ApiUserRepository
from src.repositories.mysql.orm_models.api_user_orm import ApiUserRole
from passlib.context import CryptContext
from sqlalchemy import select
from src.repositories.mysql.orm_models.api_user_orm import ApiUser
from src.repositories.mysql.orm_models.base import SessionLocal
from src.security.passwords import verify_password

bp = Blueprint('auth_routes', __name__)

# simple in-memory blocklist
_TOKEN_BLOCKLIST = set()

@bp.post('/auth/register')
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'USER')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    try:
        role_enum = ApiUserRole(role)
    except Exception:
        return jsonify({'error': 'invalid role'}), 400
    repo = ApiUserRepository()
    try:
        user = repo.create_user(username=username, password=password, role=role_enum)
        return jsonify(user), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.post('/auth/login')
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    repo = ApiUserRepository()
    # need raw object for password
    with SessionLocal() as session:
        obj = session.execute(select(ApiUser).where(ApiUser.username == username)).scalar_one_or_none()
        if not obj or not verify_password(password, obj.password_hash):
            return jsonify({'error': 'invalid credentials'}), 401
        access = create_access_token(
            identity=str(obj.api_user_id),
            expires_delta=timedelta(minutes=30),
            additional_claims={'role': obj.role.value}
        )
        refresh = create_refresh_token(
            identity=str(obj.api_user_id),
            expires_delta=timedelta(days=7),
            additional_claims={'role': obj.role.value}
        )
        return jsonify({'access_token': access, 'refresh_token': refresh}), 200

@bp.post('/auth/refresh')
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims = get_jwt() or {}
    role = claims.get('role')
    access = create_access_token(
        identity=str(identity),
        expires_delta=timedelta(minutes=30),
        additional_claims={'role': role} if role else None
    )
    return jsonify({'access_token': access}), 200

@bp.post('/auth/logout')
@jwt_required()
def logout():
    jti = get_jwt().get('jti')
    _TOKEN_BLOCKLIST.add(jti)
    return jsonify({'message': 'logged out'}), 200

# callback to check if token revoked
from flask_jwt_extended import JWTManager

def init_jwt_callbacks(jwt: JWTManager):
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_headers, jwt_payload):
        return jwt_payload.get('jti') in _TOKEN_BLOCKLIST
