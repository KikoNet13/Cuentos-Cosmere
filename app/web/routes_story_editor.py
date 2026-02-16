from __future__ import annotations

import base64
import mimetypes
import re

from flask import abort, flash, redirect, render_template, request, url_for

from ..story_store import StoryStoreError, add_slot_alternative, save_page_edits, set_slot_active
from . import web_bp
from .common import normalize_rel_path, safe_next_url
from .viewmodels import build_story_view_model


def _extract_image_payload() -> tuple[bytes | None, str, str | None]:
    uploaded = request.files.get("image_file")
    if uploaded and uploaded.filename:
        payload = uploaded.read()
        mime_type = (uploaded.mimetype or "").strip()
        if not mime_type:
            mime_type = mimetypes.guess_type(uploaded.filename)[0] or "image/png"
        if payload:
            return payload, mime_type, None

    pasted = request.form.get("pasted_image_data", "").strip()
    if not pasted:
        return None, "image/png", "No se recibio ninguna imagen."

    mime_type = "image/png"
    encoded = pasted
    if pasted.startswith("data:"):
        match = re.match(r"^data:([^;]+);base64,(.*)$", pasted, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None, "image/png", "Formato de imagen pegada invalido."
        mime_type = match.group(1).strip() or "image/png"
        encoded = match.group(2)

    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (TypeError, ValueError):
        return None, "image/png", "No se pudo decodificar la imagen pegada."

    if not decoded:
        return None, "image/png", "La imagen pegada esta vacia."

    return decoded, mime_type, None


@web_bp.get("/editor/story/<path:story_path>/page/<int:page_number>")
def story_editor_page(story_path: str, page_number: int):
    story_rel_path = normalize_rel_path(story_path)
    view_model = build_story_view_model(story_rel_path, page_number, editor_mode=True)
    if not view_model:
        abort(404)

    if view_model["page_numbers"] and int(view_model["selected_page"]) != int(page_number):
        return redirect(
            url_for(
                "web.story_editor_page",
                story_path=story_rel_path,
                page_number=int(view_model["selected_page"]),
            )
        )

    return render_template("story/editor/page.html", **view_model)


@web_bp.post("/editor/story/<path:story_path>/page/<int:page_number>/save")
@web_bp.post("/story/<path:story_path>/page/<int:page_number>/save")
def save_story_page(story_path: str, page_number: int):
    story_rel_path = normalize_rel_path(story_path)
    fallback = url_for("web.story_editor_page", story_path=story_rel_path, page_number=page_number)

    try:
        save_page_edits(
            story_rel_path=story_rel_path,
            page_number=page_number,
            text_current=request.form.get("text_current", ""),
            main_prompt_current=request.form.get("main_prompt_current", ""),
            secondary_prompt_current=request.form.get("secondary_prompt_current", None),
        )
        flash("Pagina guardada en JSON.", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/editor/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/upload")
@web_bp.post("/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/upload")
def upload_slot_image(story_path: str, page_number: int, slot_name: str):
    story_rel_path = normalize_rel_path(story_path)
    fallback = url_for("web.story_editor_page", story_path=story_rel_path, page_number=page_number)

    image_bytes, mime_type, error = _extract_image_payload()
    if error:
        flash(error, "error")
        return redirect(safe_next_url(request.form.get("next"), fallback))

    try:
        alternative = add_slot_alternative(
            story_rel_path=story_rel_path,
            page_number=page_number,
            slot_name=slot_name,
            image_bytes=image_bytes or b"",
            mime_type=mime_type,
            slug=request.form.get("alt_slug", ""),
            notes=request.form.get("alt_notes", ""),
        )
        flash(f"Alternativa creada: {alternative['id']}", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/editor/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/activate")
@web_bp.post("/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/activate")
def activate_slot_image(story_path: str, page_number: int, slot_name: str):
    story_rel_path = normalize_rel_path(story_path)
    fallback = url_for("web.story_editor_page", story_path=story_rel_path, page_number=page_number)

    alternative_id = request.form.get("alternative_id", "").strip()
    if not alternative_id:
        flash("Debe indicar alternative_id.", "error")
        return redirect(safe_next_url(request.form.get("next"), fallback))

    try:
        set_slot_active(
            story_rel_path=story_rel_path,
            page_number=page_number,
            slot_name=slot_name,
            alternative_id=alternative_id,
        )
        flash("Alternativa activa actualizada.", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))

