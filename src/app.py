import os
from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from src.repositories.mongodb.connection import init_mongo
from .api.v1.mysql.health import bp as mysql_health_bp
from .api.v1.mysql.routes import bp as mysql_routes_bp
from .api.v1.mongodb.routes import bp as mongodb_routes_bp
from .api.v1.mongodb.health import bp as mongodb_health_bp
from .api.v1.auth.routes import bp as auth_bp, init_jwt_callbacks

def create_app():
    app = Flask(__name__)

    # Initialize MongoDB connection
    init_mongo()

    # JWT configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-me')
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 1800  # 30 minutes
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 7 days
    jwt = JWTManager(app)
    init_jwt_callbacks(jwt)

    app.register_blueprint(mysql_health_bp, url_prefix="/api/v1/mysql")
    app.register_blueprint(mysql_routes_bp, url_prefix="/api/v1/mysql")

    app.register_blueprint(mongodb_health_bp, url_prefix="/api/v1/mongodb")
    app.register_blueprint(mongodb_routes_bp, url_prefix="/api/v1/mongodb")
    app.register_blueprint(auth_bp, url_prefix="/api/v1")

    @app.get("/api/v1/health")
    def health():
        return jsonify({"status": "ok"})

    # Swagger/OpenAPI docs
    SWAGGER_URL = "/api/v1/docs"
    API_URL = "/openapi/openapi.yaml"

    swaggerui_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "app_name": "Movie Rental API"
        },
    )
    app.register_blueprint(swaggerui_bp, url_prefix=SWAGGER_URL)

    @app.get(API_URL)
    def openapi_yaml():
        # Serve the static OpenAPI YAML from repo root: ../openapi/v1.yaml
        openapi_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "openapi"))
        return send_from_directory(openapi_dir, "openapi.yaml")

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5004, debug=True)
