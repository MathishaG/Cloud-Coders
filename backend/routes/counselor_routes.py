from flask import Blueprint, jsonify

counselor_bp = Blueprint("counselor_bp", __name__)


@counselor_bp.route("/", methods=["GET"])
def get_counselors():
    return jsonify({"message": "Counselor routes initialized"}), 200
