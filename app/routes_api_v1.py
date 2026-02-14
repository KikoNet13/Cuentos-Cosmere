from __future__ import annotations

import base64
import mimetypes
import re
from typing import Any

from flask import Blueprint, jsonify, request, url_for

from .catalog_provider import catalog_counts, get_node, get_story_summary, list_children
from .config import LIBRARY_ROOT
from .story_store import (
    StoryStoreError,
    add_slot_alternative,
    get_story,
    get_story_page,
    list_page_slots,
    list_story_pages,
    resolve_media_rel_path,
    save_page_edits,
    set_slot_active,
)

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

VALID_KIND_FILTERS = {"all", "node", "book", "story"}
VALID_STATUS_FILTERS = {
    "all",
    "draft",
    "text_reviewed",
    "text_blocked",
    "prompt_reviewed",
    "prompt_blocked",
    "ready",
}


def _ok(data: Any, *, status: int = 200):
    return jsonify({"ok": True, "data": data, "error": None}), status


def _error(status: int, code: str, message: str):
    return jsonify({"ok": False, "data": None, "error": {"code": code, "message": message}}), status


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _parse_positive_int(raw_value: str | None, default: int) -> int:
    try:
        value = int(str(raw_value))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _build_breadcrumbs(path_rel: str) -> list[dict[str, str]]:
    normalized = _normalize_rel_path(path_rel)
    if not normalized:
        return [{"name": "biblioteca", "path": ""}]

    crumbs = [{"name": "biblioteca", "path": ""}]
    parts = [part for part in normalized.split("/") if part]
    current: list[str] = []
    for part in parts:
        current.append(part)
        crumbs.append({"name": part, "path": "/".join(current)})
    return crumbs


def _node_type(node: dict[str, Any]) -> str:
    if bool(node.get("is_story_leaf")):
        return "story"
    if bool(node.get("is_book_node")):
        return "book"
    return "node"


def _serialize_story_summary(story: dict[str, Any]) -> dict[str, Any]:
    return {
        "story_rel_path": str(story.get("story_rel_path", "")),
        "story_id": str(story.get("story_id", "")),
        "title": str(story.get("title", "")),
        "status": str(story.get("status", "draft")),
        "book_rel_path": str(story.get("book_rel_path", "")),
        "pages": int(story.get("pages", 0)),
        "slots": int(story.get("slots", 0)),
        "alternatives": int(story.get("alternatives", 0)),
    }


def _serialize_child(node: dict[str, Any]) -> dict[str, Any]:
    node_type = _node_type(node)
    item = {
        "path_rel": str(node.get("path_rel", "")),
        "name": str(node.get("name", "")),
        "node_type": node_type,
    }

    if node_type == "story":
        story = get_story_summary(str(node.get("path_rel", "")))
        if story:
            item["story"] = _serialize_story_summary(story)
    return item


def _matches_query(item: dict[str, Any], query: str) -> bool:
    if not query:
        return True

    needle = query.lower()
    haystack = [
        str(item.get("path_rel", "")),
        str(item.get("name", "")),
        str(item.get("node_type", "")),
    ]
    story = item.get("story")
    if isinstance(story, dict):
        haystack.extend(
            [
                str(story.get("title", "")),
                str(story.get("story_id", "")),
                str(story.get("status", "")),
            ]
        )
    return any(needle in value.lower() for value in haystack)


def _apply_children_filters(
    items: list[dict[str, Any]],
    *,
    query: str,
    kind: str,
    status: str,
) -> list[dict[str, Any]]:
    filtered = items

    if kind != "all":
        filtered = [item for item in filtered if item.get("node_type") == kind]

    if status != "all":
        filtered = [
            item
            for item in filtered
            if item.get("node_type") == "story"
            and isinstance(item.get("story"), dict)
            and str(item["story"].get("status", "")).lower() == status
        ]

    if query:
        filtered = [item for item in filtered if _matches_query(item, query)]

    return filtered


def _resolve_image(rel_path: str) -> tuple[bool, str | None]:
    clean = rel_path.strip().replace("\\", "/")
    if not clean:
        return False, None

    try:
        file_path = resolve_media_rel_path(clean)
    except StoryStoreError:
        return False, None

    if not file_path.exists() or not file_path.is_file():
        return False, None
    return True, url_for("shell.media_file", rel_path=clean)


def _serialize_alternative(alternative: dict[str, Any], active_id: str) -> dict[str, Any]:
    rel_path = str(alternative.get("asset_rel_path", "")).strip().replace("\\", "/")
    image_exists, image_url = _resolve_image(rel_path)

    alt_id = str(alternative.get("id", ""))
    return {
        "id": alt_id,
        "slug": str(alternative.get("slug", "")),
        "asset_rel_path": rel_path,
        "mime_type": str(alternative.get("mime_type", "")),
        "status": str(alternative.get("status", "candidate")),
        "created_at": str(alternative.get("created_at", "")),
        "notes": str(alternative.get("notes", "")),
        "image_exists": image_exists,
        "image_url": image_url,
        "is_active": alt_id == active_id,
    }


def _definitive_image_url(alternatives: list[dict[str, Any]]) -> str | None:
    active = next(
        (item for item in alternatives if bool(item.get("is_active")) and bool(item.get("image_exists"))),
        None,
    )
    if active:
        return str(active.get("image_url") or "")

    fallback = next((item for item in alternatives if bool(item.get("image_exists"))), None)
    if fallback:
        return str(fallback.get("image_url") or "")
    return None


def _serialize_slot(slot: dict[str, Any]) -> dict[str, Any]:
    active_id = str(slot.get("active_id", ""))
    alternatives = [_serialize_alternative(item, active_id) for item in slot.get("alternatives", [])]
    definitive_image_url = _definitive_image_url(alternatives)
    if definitive_image_url == "":
        definitive_image_url = None

    return {
        "slot_name": str(slot.get("slot_name", "main")),
        "status": str(slot.get("status", "draft")),
        "prompt": {
            "original": str(slot.get("prompt_original", "")),
            "current": str(slot.get("prompt_current", "")),
        },
        "active_id": active_id,
        "definitive_image_url": definitive_image_url,
        "alternatives": alternatives,
    }


def _build_story_payload(story_rel_path: str, selected_raw: str | None) -> dict[str, Any] | None:
    story = get_story(story_rel_path)
    if not story:
        return None

    pages = list_story_pages(story_rel_path)
    page_numbers = [int(item["page_number"]) for item in pages]
    default_page = page_numbers[0] if page_numbers else 1
    selected_page = _parse_positive_int(selected_raw, default_page)
    if page_numbers and selected_page not in page_numbers:
        selected_page = default_page

    page = get_story_page(story_rel_path, selected_page) if page_numbers else None
    slots = list_page_slots(story_rel_path, selected_page) if page else []

    prev_page = None
    next_page = None
    if selected_page in page_numbers:
        idx = page_numbers.index(selected_page)
        prev_page = page_numbers[idx - 1] if idx > 0 else None
        next_page = page_numbers[idx + 1] if idx + 1 < len(page_numbers) else None

    missing_pages: list[int] = []
    if page_numbers:
        max_page = max(page_numbers)
        present = set(page_numbers)
        missing_pages = [number for number in range(1, max_page + 1) if number not in present]

    page_payload: dict[str, Any] | None = None
    if page:
        page_payload = {
            "page_number": int(page["page_number"]),
            "status": str(page.get("status", "draft")),
            "text": {
                "original": str(page.get("text_original", "")),
                "current": str(page.get("text_current", "")),
            },
            "slots": [_serialize_slot(slot) for slot in slots],
        }

    return {
        "story": {
            "story_rel_path": str(story.get("story_rel_path", "")),
            "story_id": str(story.get("story_id", "")),
            "title": str(story.get("title", "")),
            "status": str(story.get("status", "draft")),
            "schema_version": str(story.get("schema_version", "1.0")),
            "book_rel_path": str(story.get("book_rel_path", "")),
        },
        "pagination": {
            "page_numbers": page_numbers,
            "selected_page": selected_page,
            "prev_page": prev_page,
            "next_page": next_page,
            "missing_pages": missing_pages,
        },
        "page": page_payload,
        "breadcrumbs": _build_breadcrumbs(story_rel_path),
    }


def _story_error(exc: StoryStoreError):
    message = str(exc)
    lowered = message.lower()

    if "slot invalido" in lowered:
        return _error(400, "invalid_slot", message)
    if "ruta fuera del proyecto" in lowered:
        return _error(403, "forbidden_path", message)
    if "no existe pagina" in lowered:
        return _error(404, "page_not_found", message)
    if "alternativa indicada no existe" in lowered:
        return _error(409, "alternative_not_found", message)
    if "no existe cuento json" in lowered or "story_rel_path vacio" in lowered:
        return _error(404, "story_not_found", message)

    return _error(409, "story_store_error", message)


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
    if not pasted and request.is_json:
        body = request.get_json(silent=True) or {}
        pasted = str(body.get("pasted_image_data", "")).strip()

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


@api_v1_bp.get("/library/node")
def library_node():
    path_rel = _normalize_rel_path(request.args.get("path", ""))
    node = get_node(path_rel)
    if not node:
        return _error(404, "node_not_found", f"No existe el nodo: {path_rel or '<root>'}")

    kind = str(request.args.get("kind", "all")).strip().lower() or "all"
    status = str(request.args.get("status", "all")).strip().lower() or "all"
    query = str(request.args.get("q", "")).strip()

    if kind not in VALID_KIND_FILTERS:
        return _error(400, "invalid_kind_filter", f"kind invalido: {kind}")
    if status not in VALID_STATUS_FILTERS:
        return _error(400, "invalid_status_filter", f"status invalido: {status}")

    raw_children = list_children(path_rel)
    children = [_serialize_child(item) for item in raw_children]
    filtered = _apply_children_filters(children, query=query, kind=kind, status=status)

    data = {
        "node": {
            "path_rel": str(node.get("path_rel", "")),
            "name": str(node.get("name", "")),
            "node_type": _node_type(node),
        },
        "breadcrumbs": _build_breadcrumbs(path_rel),
        "children": filtered,
        "filters": {"q": query, "kind": kind, "status": status},
        "counts": catalog_counts(),
    }
    return _ok(data)


@api_v1_bp.get("/stories/<path:story_path>")
def story_detail(story_path: str):
    story_rel_path = _normalize_rel_path(story_path)
    payload = _build_story_payload(story_rel_path, request.args.get("p"))
    if not payload:
        return _error(404, "story_not_found", f"No existe el cuento: {story_rel_path}")
    return _ok(payload)


@api_v1_bp.patch("/stories/<path:story_path>/pages/<int:page_number>")
def update_story_page(story_path: str, page_number: int):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return _error(400, "invalid_json_body", "Se esperaba cuerpo JSON.")

    story_rel_path = _normalize_rel_path(story_path)
    current_page = get_story_page(story_rel_path, page_number)
    if not current_page:
        return _error(404, "page_not_found", f"No existe pagina {page_number} en {story_rel_path}.")

    slots = list_page_slots(story_rel_path, page_number)
    main_slot = next((slot for slot in slots if slot.get("slot_name") == "main"), None)
    secondary_slot = next((slot for slot in slots if slot.get("slot_name") == "secondary"), None)

    text_current = str(body.get("text_current", current_page.get("text_current", "")))
    main_prompt_current = str(
        body.get(
            "main_prompt_current",
            str(main_slot.get("prompt_current", "")) if isinstance(main_slot, dict) else "",
        )
    )

    secondary_input = body.get(
        "secondary_prompt_current",
        str(secondary_slot.get("prompt_current", "")) if isinstance(secondary_slot, dict) else None,
    )
    secondary_prompt_current = None if secondary_input is None else str(secondary_input)

    try:
        save_page_edits(
            story_rel_path=story_rel_path,
            page_number=page_number,
            text_current=text_current,
            main_prompt_current=main_prompt_current,
            secondary_prompt_current=secondary_prompt_current,
        )
    except StoryStoreError as exc:
        return _story_error(exc)

    payload = _build_story_payload(story_rel_path, str(page_number))
    if not payload:
        return _error(404, "story_not_found", f"No existe el cuento: {story_rel_path}")
    return _ok(payload)


@api_v1_bp.post("/stories/<path:story_path>/pages/<int:page_number>/slots/<slot_name>/alternatives")
def create_slot_alternative(story_path: str, page_number: int, slot_name: str):
    story_rel_path = _normalize_rel_path(story_path)
    image_bytes, mime_type, image_error = _extract_image_payload()
    if image_error:
        return _error(400, "invalid_image_payload", image_error)

    alt_slug = request.form.get("alt_slug", "")
    alt_notes = request.form.get("alt_notes", "")
    if request.is_json:
        body = request.get_json(silent=True) or {}
        alt_slug = str(body.get("alt_slug", alt_slug))
        alt_notes = str(body.get("alt_notes", alt_notes))

    try:
        add_slot_alternative(
            story_rel_path=story_rel_path,
            page_number=page_number,
            slot_name=slot_name,
            image_bytes=image_bytes or b"",
            mime_type=mime_type,
            slug=alt_slug,
            notes=alt_notes,
        )
    except StoryStoreError as exc:
        return _story_error(exc)

    payload = _build_story_payload(story_rel_path, str(page_number))
    if not payload:
        return _error(404, "story_not_found", f"No existe el cuento: {story_rel_path}")
    return _ok(payload, status=201)


@api_v1_bp.put("/stories/<path:story_path>/pages/<int:page_number>/slots/<slot_name>/active")
def set_active_alternative(story_path: str, page_number: int, slot_name: str):
    story_rel_path = _normalize_rel_path(story_path)

    alternative_id = str(request.form.get("alternative_id", "")).strip()
    if not alternative_id:
        body = request.get_json(silent=True) or {}
        alternative_id = str(body.get("alternative_id", "")).strip()
    if not alternative_id:
        return _error(400, "missing_alternative_id", "Debe indicar alternative_id.")

    try:
        set_slot_active(
            story_rel_path=story_rel_path,
            page_number=page_number,
            slot_name=slot_name,
            alternative_id=alternative_id,
        )
    except StoryStoreError as exc:
        return _story_error(exc)

    payload = _build_story_payload(story_rel_path, str(page_number))
    if not payload:
        return _error(404, "story_not_found", f"No existe el cuento: {story_rel_path}")
    return _ok(payload)


@api_v1_bp.get("/health")
def healthcheck():
    return _ok(
        {
            "library_root_exists": LIBRARY_ROOT.exists(),
            "library_root": str(LIBRARY_ROOT),
            "storage_mode": "json_fs",
        }
    )
