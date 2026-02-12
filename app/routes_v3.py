from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Any

from flask import Blueprint, abort, flash, g, jsonify, redirect, render_template, request, send_file, url_for

from .config import BASE_DIR, DATA_ROOT
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
from .library_fs import resolve_requirement_paths

web_bp = Blueprint("web", __name__)

_SLOT_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def _normalize_rel(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _slot_slug(slot_name: str) -> str:
    normalized = _SLOT_SLUG_RE.sub("-", slot_name.strip().lower())
    normalized = normalized.strip("-")
    return normalized or "slot"


def _safe_next_url(raw: str | None, fallback: str) -> str:
    value = (raw or "").strip()
    if not value.startswith("/") or value.startswith("//"):
        return fallback
    return value


def _parse_int(raw: str | None, default: int) -> int:
    try:
        value = int(str(raw))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def _breadcrumbs(path_rel: str) -> list[dict[str, str]]:
    path_norm = _normalize_rel(path_rel)
    if not path_norm:
        return [{"name": "biblioteca", "path": ""}]
    parts = [part for part in path_norm.split("/") if part]
    crumbs = [{"name": "biblioteca", "path": ""}]
    current: list[str] = []
    for part in parts:
        current.append(part)
        crumbs.append({"name": part, "path": "/".join(current)})
    return crumbs


def _story_view_model(story_path_rel: str, selected_raw: str | None) -> dict[str, Any] | None:
    story = get_story(story_path_rel)
    if not story:
        return None

    pages = list_story_pages(story_path_rel)
    page_numbers = [int(p["numero"]) for p in pages]
    if page_numbers:
        default_page = page_numbers[0]
    else:
        default_page = 1
    selected_page = _parse_int(selected_raw, default_page)
    if page_numbers and selected_page not in page_numbers:
        selected_page = default_page

    page = get_story_page(story_path_rel, selected_page) if page_numbers else None
    slot_items: list[dict[str, Any]] = []
    if page:
        for slot in list_page_slots(story_path_rel, selected_page):
            rel_path = str(slot["image_rel_path"] or "")
            image_abs = (BASE_DIR / rel_path).resolve() if rel_path else None
            exists = bool(image_abs and image_abs.exists() and image_abs.is_file())

            req_items = []
            for req in list_slot_requirements(story_path_rel, selected_page, str(slot["slot"])):
                refs: list[dict[str, Any]] = []
                for rel in resolve_requirement_paths(story_path_rel, str(req["ref"])):
                    rel_norm = rel.replace("\\", "/")
                    abs_file = (BASE_DIR / rel_norm).resolve()
                    refs.append(
                        {
                            "rel_path": rel_norm,
                            "exists": abs_file.exists() and abs_file.is_file(),
                            "url": url_for("web.media_file", rel_path=rel_norm),
                        }
                    )
                req_items.append(
                    {
                        "id": int(req["id"]),
                        "tipo": str(req["tipo"]),
                        "ref": str(req["ref"]),
                        "orden": int(req["orden"]),
                        "refs": refs,
                    }
                )

            slot_items.append(
                {
                    "slot": str(slot["slot"]),
                    "rol": str(slot["rol"]),
                    "prompt": str(slot["prompt"]),
                    "orden": int(slot["orden"]),
                    "image_rel_path": rel_path,
                    "image_exists": exists,
                    "image_url": url_for("web.media_file", rel_path=rel_path) if rel_path else "",
                    "requirements": req_items,
                }
            )

    missing_pages: list[int] = []
    if page_numbers:
        max_page = max(page_numbers)
        present = set(page_numbers)
        missing_pages = [num for num in range(1, max_page + 1) if num not in present]

    prev_page = None
    next_page = None
    if page_numbers and selected_page in page_numbers:
        idx = page_numbers.index(selected_page)
        prev_page = page_numbers[idx - 1] if idx > 0 else None
        next_page = page_numbers[idx + 1] if idx + 1 < len(page_numbers) else None

    return {
        "story": story,
        "page_numbers": page_numbers,
        "selected_page": selected_page,
        "page": page,
        "prev_page": prev_page,
        "next_page": next_page,
        "missing_pages": missing_pages,
        "slots": slot_items,
        "breadcrumbs": _breadcrumbs(story_path_rel),
    }


def _extract_image_bytes() -> tuple[bytes | None, str | None]:
    uploaded = request.files.get("image_file")
    if uploaded and uploaded.filename:
        payload = uploaded.read()
        if payload:
            return payload, None

    pasted = request.form.get("pasted_image_data", "").strip()
    if not pasted:
        return None, "No se recibió imagen."

    if pasted.startswith("data:"):
        if "," not in pasted:
            return None, "Formato de imagen pegada inválido."
        _, encoded = pasted.split(",", 1)
    else:
        encoded = pasted

    try:
        data = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError):
        return None, "No se pudo decodificar la imagen pegada."
    if not data:
        return None, "La imagen pegada está vacía."
    return data, None


def _ensure_slot_path(story_path_rel: str, page_num: int, slot_name: str, slot_rel_path: str) -> str:
    rel = slot_rel_path.strip().replace("\\", "/")
    if rel:
        return rel
    slot_slug = _slot_slug(slot_name)
    story = _normalize_rel(story_path_rel)
    return f"biblioteca/{story}/assets/imagenes/pagina-{page_num:03d}-{slot_slug}.png"


@web_bp.before_app_request
def prepare_cache_state() -> None:
    if request.endpoint and request.endpoint.startswith("web."):
        g.cache_status = ensure_cache_ready()


@web_bp.app_context_processor
def inject_cache_state() -> dict[str, Any]:
    status = getattr(g, "cache_status", None)
    if status is None:
        status = refresh_stale_flag()
    return {"cache_status": status}


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
    normalized = _normalize_rel(node_path)
    node = get_node(normalized)
    if not node:
        abort(404)
    if bool(node["is_story_leaf"]):
        return redirect(url_for("web.story_detail", story_path=normalized))

    children = list_children(normalized)
    return render_template(
        "node.html",
        node_name=str(node["nombre"]),
        node_path=normalized,
        breadcrumbs=_breadcrumbs(normalized),
        children=children,
    )


@web_bp.get("/story/<path:story_path>")
def story_detail(story_path: str):
    story_path_rel = _normalize_rel(story_path)
    vm = _story_view_model(story_path_rel, request.args.get("p"))
    if not vm:
        abort(404)
    return render_template("cuento.html", **vm)


@web_bp.post("/cache/refresh")
def cache_refresh():
    stats = rebuild_cache()
    g.cache_status = refresh_stale_flag()
    flash(
        (
            "Caché actualizada. "
            f"Cuentos: {stats['stories']} | "
            f"Páginas: {stats['pages']} | "
            f"Slots: {stats['slots']}"
        ),
        "success",
    )
    if stats["warnings"]:
        flash(f"Avisos de escaneo: {len(stats['warnings'])}", "error")
    fallback = url_for("web.dashboard")
    return redirect(_safe_next_url(request.form.get("next"), fallback))


@web_bp.get("/cache/status")
def cache_status():
    status = refresh_stale_flag()
    payload = {
        "stale": bool(status.get("stale", True)),
        "has_cache": bool(status.get("has_cache", False)),
        "last_refresh_at": status.get("last_refresh_at", ""),
        "scanned_files": int(status.get("scanned_files", 0)),
        "live_scanned_files": int(status.get("live_scanned_files", 0)),
    }
    return jsonify(payload)


@web_bp.post("/story/<path:story_path>/page/<int:page_num>/slot/<slot_name>/upload")
def upload_slot_image(story_path: str, page_num: int, slot_name: str):
    story_path_rel = _normalize_rel(story_path)
    status = refresh_stale_flag()
    if status.get("stale", True):
        flash("La caché está desactualizada. Actualiza caché antes de guardar imágenes.", "error")
        return redirect(url_for("web.story_detail", story_path=story_path_rel, p=page_num))

    story = get_story(story_path_rel)
    if not story:
        abort(404)
    page = get_story_page(story_path_rel, page_num)
    if not page:
        abort(404)
    slot = get_page_slot(story_path_rel, page_num, slot_name)
    if not slot:
        abort(404)

    data, error = _extract_image_bytes()
    if error:
        flash(error, "error")
        return redirect(url_for("web.story_detail", story_path=story_path_rel, p=page_num))

    target_rel = _ensure_slot_path(story_path_rel, page_num, slot_name, str(slot["image_rel_path"] or ""))
    target_abs = (BASE_DIR / target_rel).resolve()
    base_abs = BASE_DIR.resolve()
    if base_abs not in target_abs.parents:
        abort(403)

    target_abs.parent.mkdir(parents=True, exist_ok=True)
    target_abs.write_bytes(data)
    upsert_asset_index(target_rel)
    accept_live_fingerprint()

    flash(f"Imagen guardada en {target_rel}", "success")
    return redirect(url_for("web.story_detail", story_path=story_path_rel, p=page_num))


@web_bp.get("/media/<path:rel_path>")
def media_file(rel_path: str):
    rel = rel_path.strip().replace("\\", "/")
    target = (BASE_DIR / rel).resolve()
    base = BASE_DIR.resolve()
    if base not in target.parents and target != base:
        abort(403)
    if not target.exists() or not target.is_file():
        abort(404)
    return send_file(target)


@web_bp.get("/health")
def healthcheck():
    root_ok = DATA_ROOT.exists()
    cache_ok = Path(BASE_DIR / "db" / "library_cache.sqlite").exists()
    return jsonify({"ok": root_ok, "data_root": str(DATA_ROOT), "cache_exists": cache_ok})
