# File: app.py
# Purpose: Flask app entry point — registers all blueprints and starts server
# Step: Step-5

from flask import Flask
from flask_cors import CORS


# WHY: Import blueprints here so app.py stays thin —
# each route file owns its own logic
from routes.stats            import stats_bp
from routes.calls            import calls_bp
from routes.circuit_breakers import circuit_breakers_bp
from routes.analyze          import analyze_bp


# --- Constants ---
FLASK_PORT  = 5000
FLASK_DEBUG = True


def create_app() -> Flask:
    app = Flask(__name__)

    # WHY: CORS must be configured before any requests are handled —
    # React runs on port 5173, Flask on 5000; browser blocks cross-port requests
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    app.register_blueprint(stats_bp)
    app.register_blueprint(calls_bp)
    app.register_blueprint(circuit_breakers_bp)
    app.register_blueprint(analyze_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=FLASK_PORT, debug=FLASK_DEBUG)
