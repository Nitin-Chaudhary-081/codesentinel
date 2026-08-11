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

    from src.blueprints import auth, submissions, evaluations, reports
    app.register_blueprint(auth.bp, url_prefix="/api/v1/auth")
    app.register_blueprint(submissions.bp, url_prefix="/api/v1/submissions")
    app.register_blueprint(evaluations.bp, url_prefix="/api/v1/evaluations")
    app.register_blueprint(reports.bp, url_prefix="/api/v1/reports")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "version": __version__}

    with app.app_context():
        init_db()

    return app


app = create_app()
