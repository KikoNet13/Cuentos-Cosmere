from __future__ import annotations

from flask import abort, jsonify, send_file

from ..config import LIBRARY_ROOT
from ..story_store import StoryStoreError, resolve_media_rel_path
from . import web_bp


@web_bp.get("/media/<path:rel_path>")
def media_file(rel_path: str):
    try:
        target = resolve_media_rel_path(rel_path)
    except StoryStoreError:
        abort(403)

    if not target.exists() or not target.is_file():
        abort(404)
    return send_file(target)


@web_bp.get("/health")
def healthcheck():
    return jsonify(
        {
            "ok": LIBRARY_ROOT.exists(),
            "library_root": str(LIBRARY_ROOT),
            "storage_mode": "json_fs",
        }
    )

