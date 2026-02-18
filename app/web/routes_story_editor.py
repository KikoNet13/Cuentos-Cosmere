from __future__ import annotations

from flask import flash, redirect, request

from ..story_store import (
    StoryStoreError,
    add_anchor_alternative,
    add_cover_alternative,
    add_slot_alternative,
    save_cover_edits,
    save_page_edits,
    set_anchor_active,
    set_cover_active,
    set_slot_active,
    upsert_anchor,
)
from . import web_bp
from .common import build_story_url, first_story_page_number, normalize_rel_path, parse_positive_int, safe_next_url
from .image_upload import extract_image_payload


def _page_number(story_rel_path: str) -> int:
    return parse_positive_int(request.args.get("p"), first_story_page_number(story_rel_path))


@web_bp.post("/<path:story_path>/_act/page/save")
def save_story_page(story_path: str):
    story_rel_path = normalize_rel_path(story_path)
    page_number = _page_number(story_rel_path)
    fallback = build_story_url(story_rel_path, page_number=page_number, editor_mode=True)

    try:
        save_page_edits(
            story_rel_path=story_rel_path,
            page_number=page_number,
            text=request.form.get("text", ""),
            main_prompt=request.form.get("main_prompt", ""),
            secondary_prompt=request.form.get("secondary_prompt", None),
            main_reference_ids=request.form.get("main_reference_ids", ""),
            secondary_reference_ids=request.form.get("secondary_reference_ids", ""),
        )
        flash("Pagina guardada en JSON.", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/<path:story_path>/_act/page/slot/<slot_name>/upload")
def upload_slot_image(story_path: str, slot_name: str):
    story_rel_path = normalize_rel_path(story_path)
    page_number = _page_number(story_rel_path)
    fallback = build_story_url(story_rel_path, page_number=page_number, editor_mode=True)

    image_bytes, mime_type, error = extract_image_payload(request)
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


@web_bp.post("/<path:story_path>/_act/page/slot/<slot_name>/activate")
def activate_slot_image(story_path: str, slot_name: str):
    story_rel_path = normalize_rel_path(story_path)
    page_number = _page_number(story_rel_path)
    fallback = build_story_url(story_rel_path, page_number=page_number, editor_mode=True)

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


@web_bp.post("/<path:story_path>/_act/cover/save")
def save_story_cover(story_path: str):
    story_rel_path = normalize_rel_path(story_path)
    fallback = build_story_url(story_rel_path, editor_mode=True)

    try:
        save_cover_edits(
            story_rel_path=story_rel_path,
            prompt=request.form.get("cover_prompt", ""),
            reference_ids=request.form.get("cover_reference_ids", ""),
        )
        flash("Portada guardada.", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/<path:story_path>/_act/cover/upload")
def upload_cover_image(story_path: str):
    story_rel_path = normalize_rel_path(story_path)
    fallback = build_story_url(story_rel_path, editor_mode=True)

    image_bytes, mime_type, error = extract_image_payload(request)
    if error:
        flash(error, "error")
        return redirect(safe_next_url(request.form.get("next"), fallback))

    try:
        alternative = add_cover_alternative(
            story_rel_path=story_rel_path,
            image_bytes=image_bytes or b"",
            mime_type=mime_type,
            slug=request.form.get("alt_slug", "cover"),
            notes=request.form.get("alt_notes", ""),
        )
        flash(f"Portada alternativa creada: {alternative['id']}", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/<path:story_path>/_act/cover/activate")
def activate_cover_image(story_path: str):
    story_rel_path = normalize_rel_path(story_path)
    fallback = build_story_url(story_rel_path, editor_mode=True)

    alternative_id = request.form.get("alternative_id", "").strip()
    if not alternative_id:
        flash("Debe indicar alternative_id.", "error")
        return redirect(safe_next_url(request.form.get("next"), fallback))

    try:
        set_cover_active(story_rel_path=story_rel_path, alternative_id=alternative_id)
        flash("Portada activa actualizada.", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/<path:story_path>/_act/anchors/save")
def save_anchor(story_path: str):
    story_rel_path = normalize_rel_path(story_path)
    page_number = _page_number(story_rel_path)
    fallback = build_story_url(story_rel_path, page_number=page_number, editor_mode=True)

    anchor_level = normalize_rel_path(request.form.get("anchor_level", ""))
    anchor_id = request.form.get("anchor_id", "").strip()

    if not anchor_id:
        flash("anchor_id es obligatorio.", "error")
        return redirect(safe_next_url(request.form.get("next"), fallback))

    try:
        upsert_anchor(
            node_rel_path=anchor_level,
            anchor_id=anchor_id,
            name=request.form.get("anchor_name", "").strip(),
            prompt=request.form.get("anchor_prompt", "").strip(),
            status=request.form.get("anchor_status", "").strip() or "draft",
        )
        flash("Ancla guardada.", "success")
    except StoryStoreError as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/<path:story_path>/_act/anchors/<anchor_id>/upload")
def upload_anchor_image(story_path: str, anchor_id: str):
    story_rel_path = normalize_rel_path(story_path)
    page_number = _page_number(story_rel_path)
    fallback = build_story_url(story_rel_path, page_number=page_number, editor_mode=True)
    anchor_level = normalize_rel_path(request.form.get("anchor_level", ""))

    image_bytes, mime_type, error = extract_image_payload(request)
    if error:
        flash(error, "error")
        return redirect(safe_next_url(request.form.get("next"), fallback))

    try:
        alternative = add_anchor_alternative(
            node_rel_path=anchor_level,
            anchor_id=anchor_id,
            image_bytes=image_bytes or b"",
            mime_type=mime_type,
            slug=request.form.get("alt_slug", anchor_id),
            notes=request.form.get("alt_notes", ""),
        )
        flash(f"Alternativa de ancla creada: {alternative['id']}", "success")
    except (StoryStoreError, FileNotFoundError) as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/<path:story_path>/_act/anchors/<anchor_id>/activate")
def activate_anchor_image(story_path: str, anchor_id: str):
    story_rel_path = normalize_rel_path(story_path)
    page_number = _page_number(story_rel_path)
    fallback = build_story_url(story_rel_path, page_number=page_number, editor_mode=True)
    anchor_level = normalize_rel_path(request.form.get("anchor_level", ""))
    alternative_id = request.form.get("alternative_id", "").strip()

    if not alternative_id:
        flash("Debe indicar alternative_id.", "error")
        return redirect(safe_next_url(request.form.get("next"), fallback))

    try:
        set_anchor_active(node_rel_path=anchor_level, anchor_id=anchor_id, alternative_id=alternative_id)
        flash("Ancla activa actualizada.", "success")
    except (StoryStoreError, FileNotFoundError) as exc:
        flash(str(exc), "error")

    return redirect(safe_next_url(request.form.get("next"), fallback))
