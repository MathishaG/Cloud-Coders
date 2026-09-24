from flask import Blueprint, jsonify

prediction_bp = Blueprint("prediction_bp", __name__)


@prediction_bp.route("/predict", methods=["POST"])
def predict():
    return jsonify({"message": "Prediction route initialized"}), 200
