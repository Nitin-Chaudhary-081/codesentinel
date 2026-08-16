"""Application factory — Flask."""

from flask import Flask
from flask_cors import CORS

from src.config import settings
from src.database import init_db

__version__ = "0.1.0"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DEBUG"] = settings.debug

    CORS(app, origins=settings.cors_origins, supports_credentials=True)

    from src.blueprints.auth import bp as auth_bp
    from src.blueprints.submissions import bp as submissions_bp
    from src.blueprints.evaluations import bp as evaluations_bp
    from src.blueprints.reports import bp as reports_bp
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(submissions_bp, url_prefix="/api/v1/submissions")
    app.register_blueprint(evaluations_bp, url_prefix="/api/v1/evaluations")
    app.register_blueprint(reports_bp, url_prefix="/api/v1/reports")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "version": __version__}

    with app.app_context():
        init_db()

    return app


app = create_app()
