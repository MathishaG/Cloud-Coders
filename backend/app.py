from flask import Flask, jsonify
from flask_cors import CORS

# Import route blueprints
from routes.student_routes import student_bp
from routes.prediction_routes import prediction_bp
from routes.counselor_routes import counselor_bp
from routes.appointment_routes import appointment_bp


def create_app():
    app = Flask(__name__)

    # Enable CORS so frontend can communicate with backend
    CORS(app)

    # -----------------------------
    # Basic health/status endpoints
    # -----------------------------

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "status": "success",
            "message": "Student Risk Backend is running"
        }), 200

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy"
        }), 200

    # -----------------------------
    # Register API blueprints
    # -----------------------------

    app.register_blueprint(
        student_bp,
        url_prefix="/api/students"
    )

    app.register_blueprint(
        prediction_bp,
        url_prefix="/api"
    )

    app.register_blueprint(
        counselor_bp,
        url_prefix="/api/counselors"
    )

    app.register_blueprint(
        appointment_bp,
        url_prefix="/api/appointments"
    )

    # -----------------------------
    # 404 handler
    # -----------------------------

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Endpoint not found"
        }), 404

    # -----------------------------
    # General error handler
    # -----------------------------

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

    return app


# Create Flask application
app = create_app()


# Run application
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )