"""Application Flask de gestion des incidents informatiques."""
import os

from flask import Flask


def create_app(config=None):
    """Crée et configure l'application Flask (pattern "application factory")."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-a-changer"),
        DATABASE=os.environ.get("DATABASE_PATH", os.path.join("data", "incidents.db")),
        APP_VERSION=os.environ.get("APP_VERSION", "dev"),
    )
    if config:
        app.config.update(config)

    from . import db
    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    @app.context_processor
    def inject_version():
        return {"app_version": app.config["APP_VERSION"]}

    return app
