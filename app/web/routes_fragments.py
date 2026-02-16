from __future__ import annotations

from flask import abort, render_template, request

from ..story_store import StoryStoreError, set_slot_active
from . import web_bp
from .common import normalize_rel_path
from .viewmodels import build_story_view_model


@web_bp.get("/fragments/story/<path:story_path>/page/<int:page_number>/shell")
def story_shell_fragment(story_path: str, page_number: int):
    story_rel_path = normalize_rel_path(story_path)
    view_model = build_story_view_model(story_rel_path, page_number, editor_mode=False)
    if not view_model:
        abort(404)
    return render_template("story/read/_shell.html", **view_model)


@web_bp.get("/fragments/story/<path:story_path>/page/<int:page_number>/advanced")
def story_advanced_fragment(story_path: str, page_number: int):
    story_rel_path = normalize_rel_path(story_path)
    view_model = build_story_view_model(story_rel_path, page_number, editor_mode=False)
    if not view_model:
        abort(404)
    return render_template(
        "story/read/_advanced_panel.html",
        panel_message="",
        panel_kind="",
        **view_model,
    )


@web_bp.post("/fragments/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/activate")
def story_advanced_activate_fragment(story_path: str, page_number: int, slot_name: str):
    story_rel_path = normalize_rel_path(story_path)
    alternative_id = request.form.get("alternative_id", "").strip()

    panel_message = ""
    panel_kind = "info"
    if not alternative_id:
        panel_message = "Debe indicar una alternativa."
        panel_kind = "danger"
    else:
        try:
            set_slot_active(
                story_rel_path=story_rel_path,
                page_number=page_number,
                slot_name=slot_name,
                alternative_id=alternative_id,
            )
            panel_message = "Alternativa activa actualizada."
            panel_kind = "success"
        except StoryStoreError as exc:
            panel_message = str(exc)
            panel_kind = "danger"

    view_model = build_story_view_model(story_rel_path, page_number, editor_mode=False)
    if not view_model:
        abort(404)

    return render_template(
        "story/read/_advanced_response.html",
        panel_message=panel_message,
        panel_kind=panel_kind,
        **view_model,
    )

