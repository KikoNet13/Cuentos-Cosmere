from __future__ import annotations


def create_app():
    from flask import Flask

    from .config import APP_SECRET_KEY
    from .routes import web_bp

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = APP_SECRET_KEY
    app.register_blueprint(web_bp)
    return app
