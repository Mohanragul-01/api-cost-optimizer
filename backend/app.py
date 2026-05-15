# File: app.py
# Purpose: Flask app entry point — registers all blueprints and starts server
# Step: Step-5

import os
from flask import Flask
from flask_cors import CORS


# WHY: Import blueprints here so app.py stays thin —
# each route file owns its own logic
from routes.stats            import stats_bp
from routes.calls            import calls_bp
from routes.circuit_breakers import circuit_breakers_bp
from routes.analyze          import analyze_bp


FLASK_PORT  = int(os.environ.get("PORT", 5000))  # WHY: Render sets PORT dynamically
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"


def create_app() -> Flask:
    app = Flask(__name__)

    # WHY: CORS must be configured before any requests are handled —
    # React runs on port 5173, Flask on 5000; browser blocks cross-port requests
    allowed_origin = os.environ.get("ALLOWED_ORIGIN", "http://localhost:5173")
    CORS(app, resources={r"/api/*": {"origins": allowed_origin}})

    app.register_blueprint(stats_bp)
    app.register_blueprint(calls_bp)
    app.register_blueprint(circuit_breakers_bp)
    app.register_blueprint(analyze_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=FLASK_PORT, debug=FLASK_DEBUG)
