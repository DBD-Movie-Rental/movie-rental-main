from flask import Flask, jsonify
from .api.v1.mysql.health import bp as mysql_health_bp
from .api.v1.mysql.routes import bp as mysql_routes_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(mysql_health_bp, url_prefix="/api/v1/mysql")
    app.register_blueprint(mysql_routes_bp, url_prefix="/api/v1/mysql")

    @app.get("/api/v1/health")
    def health():
        return jsonify({"status": "ok"})

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5004, debug=True)
