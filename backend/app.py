from flask import Flask, jsonify
import os
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend.models.user_model import db
from backend.routes.auth_routes import auth
from backend.routes.dashboard_routes import dashboard
from backend.routes.page_routes import pages

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# Config
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

# Init
db.init_app(app)
JWTManager(app)
CORS(app, supports_credentials=True)

# Register routes
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(dashboard, url_prefix="/api")
app.register_blueprint(pages)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Create DB
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", "5001")))
