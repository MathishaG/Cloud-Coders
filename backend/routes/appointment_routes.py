from flask import Blueprint, jsonify

appointment_bp = Blueprint("appointment_bp", __name__)


@appointment_bp.route("/", methods=["GET"])
def get_appointments():
    return jsonify({"message": "Appointment routes initialized"}), 200
