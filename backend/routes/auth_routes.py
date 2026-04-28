from flask import Blueprint, request, jsonify
from models.user_model import db, User
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
import os

auth = Blueprint("auth", __name__)


def _business_emails():
    raw = os.getenv("BUSINESS_EMAILS", "")
    return {email.strip().lower() for email in raw.split(",") if email.strip()}

@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email", "password"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"msg": f"Missing fields: {', '.join(missing_fields)}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "User already exists"}), 400

    hashed_password = generate_password_hash(data["password"])
    normalized_email = data["email"].strip().lower()
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()

    if admin_email and normalized_email == admin_email:
        user_role = "admin"
    elif normalized_email in _business_emails():
        user_role = "business"
    else:
        user_role = "user"

    user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        role=user_role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created"}), 201


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    if not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and check_password_hash(user.password, data["password"]):
        token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role,
                "name": user.name,
            },
        )
        response = jsonify({"token": token})
        set_access_cookies(response, token)
        return response

    return jsonify({"msg": "Invalid credentials"}), 401


@auth.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200