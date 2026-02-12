from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Any

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from .config import LIBRARY_ROOT, ROOT_DIR
from .library_cache import (
    accept_live_fingerprint,
    cache_counts,
    ensure_cache_ready,
    get_node,
    get_page_slot,
    get_story,
    get_story_page,
    list_children,
    list_page_slots,
    list_slot_requirements,
    list_story_pages,
    rebuild_cache,
    refresh_stale_flag,
    upsert_asset_index,
)
from .library_fs import resolve_requirement_paths, story_rel_to_book_and_id

web_bp = Blueprint("web", __name__)

SLOT_SLUG_PATTERN = re.compile(r"[^a-z0-9-]+")


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _slot_slug(slot_name: str) -> str:
    slug = SLOT_SLUG_PATTERN.sub("-", slot_name.strip().lower()).strip("-")
    return slug or "slot"


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


def _build_story_view_model(story_rel_path: str, selected_raw: str | None) -> dict[str, Any] | None:
    story = get_story(story_rel_path)
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
            image_rel_path = str(slot["image_rel_path"] or "")
            image_abs_path = (ROOT_DIR / image_rel_path).resolve() if image_rel_path else None
            image_exists = bool(image_abs_path and image_abs_path.exists() and image_abs_path.is_file())

            requirement_items: list[dict[str, Any]] = []
            for requirement in list_slot_requirements(
                story_rel_path,
                selected_page_number,
                str(slot["slot_name"]),
            ):
                resolved_refs: list[dict[str, Any]] = []
                for rel in resolve_requirement_paths(
                    story_rel_path,
                    str(requirement["ref_value"]),
                ):
                    rel_norm = rel.replace("\\", "/")
                    abs_file = (ROOT_DIR / rel_norm).resolve()
                    resolved_refs.append(
                        {
                            "rel_path": rel_norm,
                            "exists": abs_file.exists() and abs_file.is_file(),
                            "url": url_for("web.media_file", rel_path=rel_norm),
                        }
                    )

                requirement_items.append(
                    {
                        "id": int(requirement["id"]),
                        "kind": str(requirement["requirement_kind"]),
                        "ref": str(requirement["ref_value"]),
                        "display_order": int(requirement["display_order"]),
                        "refs": resolved_refs,
                    }
                )

            slot_items.append(
                {
                    "slot_name": str(slot["slot_name"]),
                    "role": str(slot["role"]),
                    "prompt_text": str(slot["prompt_text"]),
                    "display_order": int(slot["display_order"]),
                    "image_rel_path": image_rel_path,
                    "image_exists": image_exists,
                    "image_url": (
                        url_for("web.media_file", rel_path=image_rel_path)
                        if image_rel_path
                        else ""
                    ),
                    "requirements": requirement_items,
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
    }


def _extract_image_bytes() -> tuple[bytes | None, str | None]:
    uploaded = request.files.get("image_file")
    if uploaded and uploaded.filename:
        payload = uploaded.read()
        if payload:
            return payload, None

    pasted = request.form.get("pasted_image_data", "").strip()
    if not pasted:
        return None, "No se recibió ninguna imagen."

    if pasted.startswith("data:"):
        if "," not in pasted:
            return None, "Formato de imagen pegada inválido."
        _, encoded = pasted.split(",", 1)
    else:
        encoded = pasted

    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (TypeError, ValueError):
        return None, "No se pudo decodificar la imagen pegada."

    if not decoded:
        return None, "La imagen pegada está vacía."
    return decoded, None


def _resolve_slot_target_path(
    story_rel_path: str,
    page_number: int,
    slot_name: str,
    cached_rel_path: str,
) -> str:
    rel = cached_rel_path.strip().replace("\\", "/")
    if rel:
        return rel

    book_rel_path, story_id = story_rel_to_book_and_id(story_rel_path)
    slot_slug = _slot_slug(slot_name)
    if book_rel_path:
        return f"library/{book_rel_path}/{story_id}-p{page_number:02d}-{slot_slug}.png"
    return f"library/{story_id}-p{page_number:02d}-{slot_slug}.png"


@web_bp.before_app_request
def _prepare_cache_state() -> None:
    if request.endpoint and request.endpoint.startswith("web."):
        g.cache_state = ensure_cache_ready()


@web_bp.app_context_processor
def _inject_cache_state() -> dict[str, Any]:
    state = getattr(g, "cache_state", None)
    if state is None:
        state = refresh_stale_flag()
    return {"cache_status": state}


@web_bp.get("/")
def dashboard():
    counts = cache_counts()
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
    view_model = _build_story_view_model(story_rel_path, request.args.get("p"))
    if not view_model:
        abort(404)
    return render_template("cuento.html", **view_model)


@web_bp.post("/cache/refresh")
def cache_refresh():
    stats = rebuild_cache()
    g.cache_state = refresh_stale_flag()

    flash(
        (
            "Caché actualizada. "
            f"Cuentos: {stats['stories']} | "
            f"Páginas: {stats['pages']} | "
            f"Slots: {stats['slots']}"
        ),
        "success",
    )
    if stats.get("warnings"):
        flash(f"Avisos de escaneo: {len(stats['warnings'])}", "error")

    fallback = url_for("web.dashboard")
    return redirect(_safe_next_url(request.form.get("next"), fallback))


@web_bp.get("/cache/status")
def cache_status():
    state = refresh_stale_flag()
    payload = {
        "stale": bool(state.get("stale", True)),
        "has_cache": bool(state.get("has_cache", False)),
        "last_refresh_at": state.get("last_refresh_at", ""),
        "scanned_files": int(state.get("scanned_files", 0)),
        "live_scanned_files": int(state.get("live_scanned_files", 0)),
        "cache_backend": state.get("cache_backend", ""),
    }
    return jsonify(payload)


@web_bp.post("/story/<path:story_path>/page/<int:page_number>/slot/<slot_name>/upload")
def upload_slot_image(story_path: str, page_number: int, slot_name: str):
    story_rel_path = _normalize_rel_path(story_path)
    state = refresh_stale_flag()
    if state.get("stale", True):
        flash("La caché está desactualizada. Actualiza la caché antes de guardar imágenes.", "error")
        return redirect(url_for("web.story_detail", story_path=story_rel_path, p=page_number))

    story = get_story(story_rel_path)
    if not story:
        abort(404)

    page = get_story_page(story_rel_path, page_number)
    if not page:
        abort(404)

    slot = get_page_slot(story_rel_path, page_number, slot_name)
    if not slot:
        abort(404)

    image_bytes, error = _extract_image_bytes()
    if error:
        flash(error, "error")
        return redirect(url_for("web.story_detail", story_path=story_rel_path, p=page_number))

    target_rel_path = _resolve_slot_target_path(
        story_rel_path=story_rel_path,
        page_number=page_number,
        slot_name=slot_name,
        cached_rel_path=str(slot["image_rel_path"] or ""),
    )
    target_abs_path = (ROOT_DIR / target_rel_path).resolve()

    root_abs_path = ROOT_DIR.resolve()
    if root_abs_path not in target_abs_path.parents:
        abort(403)

    target_abs_path.parent.mkdir(parents=True, exist_ok=True)
    target_abs_path.write_bytes(image_bytes or b"")

    upsert_asset_index(target_rel_path)
    accept_live_fingerprint()

    flash(f"Imagen guardada en {target_rel_path}", "success")
    return redirect(url_for("web.story_detail", story_path=story_rel_path, p=page_number))


@web_bp.get("/media/<path:rel_path>")
def media_file(rel_path: str):
    normalized = rel_path.strip().replace("\\", "/")
    target = (ROOT_DIR / normalized).resolve()

    root_abs = ROOT_DIR.resolve()
    if root_abs not in target.parents and target != root_abs:
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
            "cache_db": str((ROOT_DIR / "db" / "library_cache.sqlite")),
        }
    )
