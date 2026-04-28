from flask import Blueprint, send_from_directory, redirect
import os
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

pages = Blueprint("pages", __name__)
ALLOWED_DASHBOARD_ROLES = {"admin", "business"}

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))


def _current_user_role():
    try:
        return get_jwt().get("role")
    except Exception:
        return None


@pages.route("/")
def landing_page():
    return send_from_directory(FRONTEND_DIR, "index.html")


@pages.route("/login")
def login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")


@pages.route("/signup")
def signup_page():
    return send_from_directory(FRONTEND_DIR, "signup.html")


@pages.route("/dashboard")
def dashboard_page():
    try:
        verify_jwt_in_request(optional=True, locations=["cookies"])
    except Exception:
        return redirect("/login")

    user_id = get_jwt_identity()
    if not user_id:
        return redirect("/login")

    if _current_user_role() not in ALLOWED_DASHBOARD_ROLES:
        return redirect("/")

    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@pages.route("/segments")
def segments_page():
    try:
        verify_jwt_in_request(optional=True, locations=["cookies"])
    except Exception:
        return redirect("/login")

    user_id = get_jwt_identity()
    if not user_id:
        return redirect("/login")

    if _current_user_role() not in ALLOWED_DASHBOARD_ROLES:
        return redirect("/")

    return send_from_directory(FRONTEND_DIR, "segments.html")
