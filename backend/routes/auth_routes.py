from flask import Blueprint, request, jsonify
from models.user_model import db, User
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
import os

auth = Blueprint("auth", __name__)

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
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    user_role = "admin" if admin_email and data["email"].strip().lower() == admin_email else "user"

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
        token = create_access_token(identity={
            "id": user.id,
            "role": user.role
        })
        response = jsonify({"token": token})
        set_access_cookies(response, token)
        return response

    return jsonify({"msg": "Invalid credentials"}), 401


@auth.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "Logged out"})
    unset_jwt_cookies(response)
    return response, 200