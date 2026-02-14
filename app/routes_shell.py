from __future__ import annotations

from flask import Blueprint, abort, redirect, render_template, send_file, url_for

from .story_store import StoryStoreError, resolve_media_rel_path

shell_bp = Blueprint("shell", __name__)


@shell_bp.get("/")
def root_redirect():
    return redirect(url_for("shell.library_root"))


@shell_bp.get("/biblioteca")
def library_root():
    return render_template("spa_shell.html")


@shell_bp.get("/biblioteca/<path:node_path>")
def library_node(node_path: str):
    return render_template("spa_shell.html")


@shell_bp.get("/cuento/<path:story_path>")
def story_view(story_path: str):
    return render_template("spa_shell.html")


@shell_bp.get("/media/<path:rel_path>")
def media_file(rel_path: str):
    try:
        target = resolve_media_rel_path(rel_path)
    except StoryStoreError:
        abort(403)

    if not target.exists() or not target.is_file():
        abort(404)
    return send_file(target)
