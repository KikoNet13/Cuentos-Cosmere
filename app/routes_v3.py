from __future__ import annotations

import base64
import mimetypes
import re
from typing import Any

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, send_file, url_for

from .catalog_provider import catalog_counts, get_node, get_story_summary, list_children
from .config import LIBRARY_ROOT
from .story_store import (
    StoryStoreError,
    add_slot_alternative,
    get_story_page,
    list_page_slots,
    list_story_pages,
    resolve_media_rel_path,
    save_page_edits,
    set_slot_active,
)

web_bp = Blueprint("web", __name__)


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _safe_next_url(raw_value: str | None, fallback_url: str) -> str:
    value = (raw_value or "").strip()
    if not value.startswith("/") or value.startswith("//"):
        return fallback_url
    return value


def _parse_positive_int(raw_value: str | None, default: int) -> int:
    try:
        value = int(str(raw_value))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _is_editor_mode(raw_value: str | None) -> bool:
    value = (raw_value or "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _build_breadcrumbs(path_rel: str) -> list[dict[str, str]]:
    normalized = _normalize_rel_path(path_rel)
    if not normalized:
        return [{"name": "biblioteca", "path": ""}]

    parts = [part for part in normalized.split("/") if part]
    crumbs = [{"name": "biblioteca", "path": ""}]
    current: list[str] = []
    for part in parts:
        current.append(part)
        crumbs.append({"name": part, "path": "/".join(current)})
    return crumbs


def _build_alternative_view(alternative: dict[str, Any], active_id: str) -> dict[str, Any]:
    rel_path = str(alternative.get("asset_rel_path", "")).strip().replace("\\", "/")

    image_exists = False
    image_url = ""
    if rel_path:
        try:
            target = resolve_media_rel_path(rel_path)
            image_exists = target.exists() and target.is_file()
            if image_exists:
                image_url = url_for("web.media_file", rel_path=rel_path)
        except StoryStoreError:
            image_exists = False

    return {
        "id": str(alternative.get("id", "")),
        "slug": str(alternative.get("slug", "")),
        "asset_rel_path": rel_path,
        "mime_type": str(alternative.get("mime_type", "")),
        "status": str(alternative.get("status", "candidate")),
        "created_at": str(alternative.get("created_at", "")),
        "notes": str(alternative.get("notes", "")),
        "is_active": str(alternative.get("id", "")) == active_id,
        "image_exists": image_exists,
        "image_url": image_url,
    }


def _build_story_view_model(
    story_rel_path: str,
    selected_raw: str | None,
    *,
    editor_mode: bool,
) -> dict[str, Any] | None:
    story = get_story_summary(story_rel_path)
    if not story:
        return None

    pages = list_story_pages(story_rel_path)
    page_numbers = [int(page["page_number"]) for page in pages]
    default_page_number = page_numbers[0] if page_numbers else 1

    selected_page_number = _parse_positive_int(selected_raw, default_page_number)
    if page_numbers and selected_page_number not in page_numbers:
        selected_page_number = default_page_number

    page = get_story_page(story_rel_path, selected_page_number) if page_numbers else None

    slot_items: list[dict[str, Any]] = []
    if page:
        for slot in list_page_slots(story_rel_path, selected_page_number):
            active_id = str(slot.get("active_id", ""))
            alternatives = [_build_alternative_view(item, active_id) for item in slot.get("alternatives", [])]
            active_item = next((item for item in alternatives if item["is_active"]), None)

            slot_items.append(
                {
                    "slot_name": str(slot.get("slot_name", "main")),
                    "status": str(slot.get("status", "draft")),
                    "prompt_current": str(slot.get("prompt_current", "")),
                    "prompt_original": str(slot.get("prompt_original", "")),
                    "active_id": active_id,
                    "active_item": active_item,
                    "alternatives": alternatives,
                }
            )

    missing_pages: list[int] = []
    if page_numbers:
        max_page = max(page_numbers)
        present = set(page_numbers)
        missing_pages = [value for value in range(1, max_page + 1) if value not in present]

    prev_page = None
    next_page = None
    if page_numbers and selected_page_number in page_numbers:
        index = page_numbers.index(selected_page_number)
        prev_page = page_numbers[index - 1] if index > 0 else None
        next_page = page_numbers[index + 1] if index + 1 < len(page_numbers) else None

    return {
        "story": story,
        "page_numbers": page_numbers,
        "selected_page": selected_page_number,
        "page": page,
        "prev_page": prev_page,
        "next_page": next_page,
        "missing_pages": missing_pages,
        "slots": slot_items,
        "breadcrumbs": _build_breadcrumbs(story_rel_path),
        "editor_mode": editor_mode,
    }


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


@web_bp.get("/")
def dashboard():
    counts = catalog_counts()
    children = list_children("")
    return render_template(
        "dashboard.html",
        node_name="biblioteca",
        node_path="",
        breadcrumbs=[{"name": "biblioteca", "path": ""}],
        children=children,
        counts=counts,
    )


@web_bp.get("/n/<path:node_path>")
def node_detail(node_path: str):
    normalized = _normalize_rel_path(node_path)
    node = get_node(normalized)
    if not node:
        abort(404)

    if bool(node["is_story_leaf"]):
        return redirect(url_for("web.story_detail", story_path=normalized))

    children = list_children(normalized)
    return render_template(
        "node.html",
        node_name=str(node["name"]),
        node_path=normalized,
        breadcrumbs=_build_breadcrumbs(normalized),
        children=children,
    )


@web_bp.get("/story/<path:story_path>")
def story_detail(story_path: str):
    story_rel_path = _normalize_rel_path(story_path)
    editor_mode = _is_editor_mode(request.args.get("editor"))
    view_model = _build_story_view_model(story_rel_path, request.args.get("p"), editor_mode=editor_mode)
    if not view_model:
        abort(404)
    template_name = "cuento_editor.html" if editor_mode else "cuento_read.html"
    return render_template(template_name, **view_model)


@web_bp.post("/story/<path:story_path>/page/<int:page_number>/save")
def save_story_page(story_path: str, page_number: int):
    story_rel_path = _normalize_rel_path(story_path)
    fallback = url_for("web.story_detail", story_path=story_rel_path, p=page_number, editor=1)

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

    return redirect(_safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/upload")
def upload_slot_image(story_path: str, page_number: int, slot_name: str):
    story_rel_path = _normalize_rel_path(story_path)
    fallback = url_for("web.story_detail", story_path=story_rel_path, p=page_number, editor=1)

    image_bytes, mime_type, error = _extract_image_payload()
    if error:
        flash(error, "error")
        return redirect(_safe_next_url(request.form.get("next"), fallback))

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

    return redirect(_safe_next_url(request.form.get("next"), fallback))


@web_bp.post("/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/activate")
def activate_slot_image(story_path: str, page_number: int, slot_name: str):
    story_rel_path = _normalize_rel_path(story_path)
    fallback = url_for("web.story_detail", story_path=story_rel_path, p=page_number, editor=1)

    alternative_id = request.form.get("alternative_id", "").strip()
    if not alternative_id:
        flash("Debe indicar alternative_id.", "error")
        return redirect(_safe_next_url(request.form.get("next"), fallback))

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

    return redirect(_safe_next_url(request.form.get("next"), fallback))


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
