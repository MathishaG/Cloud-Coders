from flask import Blueprint, jsonify

student_bp = Blueprint("student_bp", __name__)


@student_bp.route("/", methods=["GET"])
def get_students():
    return jsonify({"message": "Student routes initialized"}), 200
