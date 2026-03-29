from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ml.predict import predict_from_payload
from ml.segment import segment_from_payload, get_segment_summary

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard_home():
    user = get_jwt_identity()
    if user.get("role") != "admin":
        return jsonify({"msg": "Admins only"}), 403

    return jsonify({
        "msg": "Welcome to dashboard",
        "user": user
    })


@dashboard.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    user = get_jwt_identity()
    if user.get("role") != "admin":
        return jsonify({"msg": "Admins only"}), 403

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
    user = get_jwt_identity()
    if user.get("role") != "admin":
        return jsonify({"msg": "Admins only"}), 403

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
    user = get_jwt_identity()
    if user.get("role") != "admin":
        return jsonify({"msg": "Admins only"}), 403

    try:
        summary = get_segment_summary()
    except FileNotFoundError as exc:
        return jsonify({"msg": str(exc)}), 503

    return jsonify(summary)