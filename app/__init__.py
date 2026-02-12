from __future__ import annotations


def create_app():
    from flask import Flask

    from .routes import web_bp

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "cosmere-local-dev"
    app.register_blueprint(web_bp)
    return app
