from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from ml.predict import predict_from_payload
from ml.segment import segment_from_payload, get_segment_summary

dashboard = Blueprint("dashboard", __name__)
ALLOWED_DASHBOARD_ROLES = {"admin", "business"}


def _current_user_context():
    claims = get_jwt()
    return {
        "id": int(get_jwt_identity()),
        "role": claims.get("role"),
        "name": claims.get("name"),
    }


def _require_dashboard_role(user):
    if user.get("role") in ALLOWED_DASHBOARD_ROLES:
        return None
    return jsonify({"msg": "Access denied. Dashboard is available to business users only."}), 403

@dashboard.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard_home():
    user = _current_user_context()
    forbidden = _require_dashboard_role(user)
    if forbidden:
        return forbidden

    return jsonify({
        "msg": "Welcome to dashboard",
        "user": user
    })


@dashboard.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    user = _current_user_context()
    forbidden = _require_dashboard_role(user)
    if forbidden:
        return forbidden

    body = request.get_json(silent=True) or {}
    payload = body.get("features")

    if not isinstance(payload, dict):
        return jsonify({"msg": "Request body must include a 'features' object"}), 400

    try:
        result = predict_from_payload(payload)
    except ValueError as exc:
        return jsonify({"msg": str(exc)}), 400

    return jsonify(result)


@dashboard.route("/segment", methods=["POST"])
@jwt_required()
def segment_customer():
    user = _current_user_context()
    forbidden = _require_dashboard_role(user)
    if forbidden:
        return forbidden

    body = request.get_json(silent=True) or {}
    payload = body.get("features")

    if not isinstance(payload, dict):
        return jsonify({"msg": "Request body must include a 'features' object"}), 400

    try:
        result = segment_from_payload(payload)
    except ValueError as exc:
        return jsonify({"msg": str(exc)}), 400
    except FileNotFoundError as exc:
        return jsonify({"msg": str(exc)}), 503

    return jsonify(result)


@dashboard.route("/segments/summary", methods=["GET"])
@jwt_required()
def segment_summary():
    user = _current_user_context()
    forbidden = _require_dashboard_role(user)
    if forbidden:
        return forbidden

    try:
        summary = get_segment_summary()
    except FileNotFoundError as exc:
        return jsonify({"msg": str(exc)}), 503

    return jsonify(summary)