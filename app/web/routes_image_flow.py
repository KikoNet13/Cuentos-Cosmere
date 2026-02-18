from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for

from ..story_store import (
    StoryStoreError,
    add_anchor_alternative,
    add_cover_alternative,
    add_slot_alternative,
    set_anchor_active,
    set_cover_active,
    set_slot_active,
)
from . import web_bp
from .common import build_story_url, normalize_rel_path, parse_positive_int
from .image_flow import build_image_flow_snapshot
from .image_upload import extract_image_payload


def _item_editor_url(item: dict[str, object]) -> str:
    item_type = str(item.get("item_type", ""))
    story_rel_path = normalize_rel_path(str(item.get("story_rel_path", "")))

    if item_type == "anchor":
        editor_story_rel_path = normalize_rel_path(str(item.get("editor_story_rel_path", "")))
        if editor_story_rel_path:
            editor_page = parse_positive_int(str(item.get("editor_page", "1")), 1)
            return build_story_url(editor_story_rel_path, page_number=editor_page, editor_mode=True)
        return url_for("web.dashboard")

    if item_type == "cover" and story_rel_path:
        return build_story_url(story_rel_path, editor_mode=True)

    if item_type == "slot" and story_rel_path:
        page_number = parse_positive_int(str(item.get("page_number", "1")), 1)
        return build_story_url(story_rel_path, page_number=page_number, editor_mode=True)

    return url_for("web.dashboard")


def _with_reference_urls(item: dict[str, object]) -> dict[str, object]:
    result = dict(item)
    refs = []
    for raw_ref in list(result.get("reference_assets", [])):
        if not isinstance(raw_ref, dict):
            continue
        row = dict(raw_ref)
        asset_rel_path = str(row.get("asset_rel_path", "")).strip()
        row["image_url"] = url_for("web.media_file", rel_path=asset_rel_path) if row.get("found") and asset_rel_path else ""
        refs.append(row)
    result["reference_assets"] = refs
    result["editor_url"] = _item_editor_url(result)
    return result


@web_bp.get("/_flow/image")
def image_flow_page():
    snapshot = build_image_flow_snapshot()
    pending_items = snapshot.get("pending_items", [])
    current_item = _with_reference_urls(pending_items[0]) if pending_items else None

    return render_template(
        "story/flow/image_fill.html",
        current_item=current_item,
        pending_count=int(snapshot.get("pending_count", 0) or 0),
        completed_count=int(snapshot.get("completed_count", 0) or 0),
        excluded_no_prompt_count=int(snapshot.get("excluded_no_prompt_count", 0) or 0),
        excluded_no_prompt=list(snapshot.get("excluded_no_prompt", [])),
    )


@web_bp.post("/_flow/image/submit")
def image_flow_submit():
    image_bytes, mime_type, error = extract_image_payload(request)
    if error:
        flash(error, "error")
        return redirect(url_for("web.image_flow_page"))

    item_type = request.form.get("item_type", "").strip().lower()
    notes = "Flujo guiado de imagenes pendientes"

    try:
        if item_type == "anchor":
            anchor_node_rel_path = normalize_rel_path(request.form.get("anchor_node_rel_path", ""))
            anchor_id = request.form.get("anchor_id", "").strip()
            if not anchor_id:
                raise StoryStoreError("anchor_id es obligatorio para guardar ancla.")

            slug = request.form.get("alt_slug", "").strip() or f"flow-{anchor_id}"
            alternative = add_anchor_alternative(
                node_rel_path=anchor_node_rel_path,
                anchor_id=anchor_id,
                image_bytes=image_bytes or b"",
                mime_type=mime_type,
                slug=slug,
                notes=notes,
            )
            set_anchor_active(
                node_rel_path=anchor_node_rel_path,
                anchor_id=anchor_id,
                alternative_id=str(alternative.get("id", "")),
            )
            flash(f"Ancla actualizada: {anchor_id}", "success")
            return redirect(url_for("web.image_flow_page"))

        if item_type == "cover":
            story_rel_path = normalize_rel_path(request.form.get("story_rel_path", ""))
            if not story_rel_path:
                raise StoryStoreError("story_rel_path es obligatorio para portada.")

            slug = request.form.get("alt_slug", "").strip() or "cover-flow"
            alternative = add_cover_alternative(
                story_rel_path=story_rel_path,
                image_bytes=image_bytes or b"",
                mime_type=mime_type,
                slug=slug,
                notes=notes,
            )
            set_cover_active(
                story_rel_path=story_rel_path,
                alternative_id=str(alternative.get("id", "")),
            )
            flash(f"Portada actualizada: {story_rel_path}", "success")
            return redirect(url_for("web.image_flow_page"))

        if item_type == "slot":
            story_rel_path = normalize_rel_path(request.form.get("story_rel_path", ""))
            page_number = parse_positive_int(request.form.get("page_number", "1"), 1)
            slot_name = request.form.get("slot_name", "").strip().lower()
            if not story_rel_path:
                raise StoryStoreError("story_rel_path es obligatorio para slot de pagina.")
            if slot_name not in {"main", "secondary"}:
                raise StoryStoreError("slot_name invalido para guardado rapido.")

            slug = request.form.get("alt_slug", "").strip() or f"p{page_number:02d}-{slot_name}-flow"
            alternative = add_slot_alternative(
                story_rel_path=story_rel_path,
                page_number=page_number,
                slot_name=slot_name,
                image_bytes=image_bytes or b"",
                mime_type=mime_type,
                slug=slug,
                notes=notes,
            )
            set_slot_active(
                story_rel_path=story_rel_path,
                page_number=page_number,
                slot_name=slot_name,
                alternative_id=str(alternative.get("id", "")),
            )
            flash(f"Slot actualizado: {story_rel_path} pagina {page_number} ({slot_name})", "success")
            return redirect(url_for("web.image_flow_page"))

        flash("item_type invalido para guardado rapido.", "error")
        return redirect(url_for("web.image_flow_page"))
    except (StoryStoreError, FileNotFoundError) as exc:
        flash(str(exc), "error")
        return redirect(url_for("web.image_flow_page"))
