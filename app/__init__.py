from __future__ import annotations


def create_app():
    from flask import Flask, flash, redirect, request, url_for
    from werkzeug.exceptions import RequestEntityTooLarge

    from .config import APP_SECRET_KEY, UPLOAD_MAX_BYTES
    from .web import web_bp

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = APP_SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = UPLOAD_MAX_BYTES
    app.config["MAX_FORM_MEMORY_SIZE"] = UPLOAD_MAX_BYTES

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_entity_too_large(_exc: RequestEntityTooLarge):
        max_mb = UPLOAD_MAX_BYTES // (1024 * 1024)
        flash(f"La imagen supera el limite de {max_mb} MB.", "error")
        if request.referrer:
            return redirect(request.referrer)
        try:
            return redirect(url_for("web.image_flow_page"))
        except Exception:
            return redirect("/")

    app.register_blueprint(web_bp)
    return app
