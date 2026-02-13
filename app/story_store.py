from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT, ROOT_DIR

STORY_JSON_RE = re.compile(r"^(\d{2})\.json$", re.IGNORECASE)
SLOT_NAMES = ("main", "secondary")


class StoryStoreError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _normalize_slot_name(slot_name: str) -> str:
    value = slot_name.strip().lower()
    if value not in SLOT_NAMES:
        raise StoryStoreError(f"slot invalido: {slot_name}")
    return value


def _normalize_slug(slug: str, fallback: str) -> str:
    value = re.sub(r"[^a-z0-9-]+", "-", slug.lower().strip())
    value = value.strip("-")
    if value:
        return value
    return fallback


def _slot_default(slot_name: str) -> dict[str, Any]:
    return {
        "slot_name": slot_name,
        "status": "draft",
        "prompt": {
            "original": "",
            "current": "",
        },
        "active_id": "",
        "alternatives": [],
    }


def _coerce_alternative(raw_value: Any) -> dict[str, Any] | None:
    if not isinstance(raw_value, dict):
        return None

    alt_id = str(raw_value.get("id", "")).strip()
    if not alt_id:
        return None

    return {
        "id": alt_id,
        "slug": str(raw_value.get("slug", "")).strip(),
        "asset_rel_path": str(raw_value.get("asset_rel_path", "")).strip().replace("\\", "/"),
        "mime_type": str(raw_value.get("mime_type", "")).strip() or "image/png",
        "status": str(raw_value.get("status", "")).strip() or "candidate",
        "created_at": str(raw_value.get("created_at", "")).strip() or _utc_now_iso(),
        "notes": str(raw_value.get("notes", "")).strip(),
    }


def _coerce_slot(raw_value: Any, slot_name: str) -> dict[str, Any]:
    base = _slot_default(slot_name)
    if not isinstance(raw_value, dict):
        return base

    prompt_raw = raw_value.get("prompt", {})
    if isinstance(prompt_raw, dict):
        base["prompt"] = {
            "original": str(prompt_raw.get("original", "")),
            "current": str(prompt_raw.get("current", "")),
        }

    status = str(raw_value.get("status", "")).strip()
    if status:
        base["status"] = status

    alternatives: list[dict[str, Any]] = []
    for item in raw_value.get("alternatives", []):
        alt = _coerce_alternative(item)
        if alt:
            alternatives.append(alt)

    base["alternatives"] = alternatives

    active_id = str(raw_value.get("active_id", "")).strip()
    if active_id and any(item["id"] == active_id for item in alternatives):
        base["active_id"] = active_id
    elif alternatives:
        base["active_id"] = alternatives[0]["id"]

    return base


def _coerce_page(raw_value: Any, fallback_number: int) -> dict[str, Any]:
    if not isinstance(raw_value, dict):
        raw_value = {}

    try:
        page_number = int(raw_value.get("page_number", fallback_number))
    except (TypeError, ValueError):
        page_number = fallback_number
    if page_number <= 0:
        page_number = fallback_number

    text_raw = raw_value.get("text", {})
    if not isinstance(text_raw, dict):
        text_raw = {}

    images_raw = raw_value.get("images", {})
    if not isinstance(images_raw, dict):
        images_raw = {}

    page = {
        "page_number": page_number,
        "status": str(raw_value.get("status", "")).strip() or "draft",
        "text": {
            "original": str(text_raw.get("original", "")),
            "current": str(text_raw.get("current", "")),
        },
        "images": {
            "main": _coerce_slot(images_raw.get("main", {}), "main"),
        },
    }

    secondary_slot = _coerce_slot(images_raw.get("secondary", None), "secondary")
    has_secondary = bool(
        secondary_slot["prompt"]["original"].strip()
        or secondary_slot["prompt"]["current"].strip()
        or secondary_slot["alternatives"]
    )
    if "secondary" in images_raw or has_secondary:
        page["images"]["secondary"] = secondary_slot

    return page


def _coerce_story_payload(payload: Any, *, story_id_hint: str, book_rel_path_hint: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StoryStoreError("El contenido del cuento debe ser un objeto JSON.")

    story_id = str(payload.get("story_id", "")).strip() or story_id_hint
    if not re.fullmatch(r"\d{2}", story_id):
        raise StoryStoreError("story_id invalido en JSON.")

    title = str(payload.get("title", "")).strip() or f"Cuento {story_id}"
    book_rel_path = _normalize_rel_path(str(payload.get("book_rel_path", "")).strip() or book_rel_path_hint)

    pages_raw = payload.get("pages", [])
    if not isinstance(pages_raw, list):
        raise StoryStoreError("pages debe ser una lista.")

    pages: list[dict[str, Any]] = []
    for index, item in enumerate(pages_raw, start=1):
        pages.append(_coerce_page(item, index))

    pages.sort(key=lambda item: int(item["page_number"]))

    created_at = str(payload.get("created_at", "")).strip() or _utc_now_iso()
    updated_at = str(payload.get("updated_at", "")).strip() or created_at

    return {
        "schema_version": str(payload.get("schema_version", "")).strip() or "1.0",
        "story_id": story_id,
        "title": title,
        "status": str(payload.get("status", "")).strip() or "draft",
        "book_rel_path": book_rel_path,
        "created_at": created_at,
        "updated_at": updated_at,
        "pages": pages,
    }


def story_rel_to_json_path(story_rel_path: str) -> Path:
    normalized = _normalize_rel_path(story_rel_path)
    if not normalized:
        raise StoryStoreError("story_rel_path vacio.")
    return LIBRARY_ROOT / f"{normalized}.json"


def json_path_to_story_rel(json_file: Path) -> str:
    rel = json_file.resolve().relative_to(LIBRARY_ROOT.resolve()).as_posix()
    if not rel.lower().endswith(".json"):
        raise StoryStoreError("archivo no es JSON de cuento")
    return rel[:-5]


def list_story_json_files() -> list[Path]:
    matches: list[Path] = []
    if not LIBRARY_ROOT.exists():
        return matches

    for entry in LIBRARY_ROOT.rglob("*.json"):
        if not entry.is_file():
            continue

        rel_parts = entry.resolve().relative_to(LIBRARY_ROOT.resolve()).parts
        if rel_parts and rel_parts[0] in {"_inbox", "_backups"}:
            continue

        if not STORY_JSON_RE.fullmatch(entry.name):
            continue

        matches.append(entry)

    matches.sort(key=lambda item: item.as_posix())
    return matches


def _read_story_file(story_file: Path) -> dict[str, Any]:
    if not story_file.exists() or not story_file.is_file():
        raise FileNotFoundError(f"No existe cuento JSON: {story_file}")

    try:
        payload = json.loads(story_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StoryStoreError(f"JSON invalido en {story_file}: {exc}") from exc

    story_id_hint = story_file.stem
    book_rel_hint = (
        story_file.parent.resolve().relative_to(LIBRARY_ROOT.resolve()).as_posix()
        if story_file.parent.resolve() != LIBRARY_ROOT.resolve()
        else ""
    )
    return _coerce_story_payload(payload, story_id_hint=story_id_hint, book_rel_path_hint=book_rel_hint)


def _write_story_file(story_file: Path, payload: dict[str, Any]) -> None:
    story_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = story_file.with_suffix(story_file.suffix + ".tmp")
    content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    try:
        temp_file.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise StoryStoreError(f"No se pudo escribir temporal JSON: {exc}") from exc

    try:
        temp_file.replace(story_file)
    except OSError:
        try:
            story_file.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise StoryStoreError(f"No se pudo guardar JSON de cuento: {exc}") from exc
        finally:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except OSError:
                pass


def load_story(story_rel_path: str) -> dict[str, Any]:
    story_file = story_rel_to_json_path(story_rel_path)
    return _read_story_file(story_file)


def get_story(story_rel_path: str) -> dict[str, Any] | None:
    try:
        payload = load_story(story_rel_path)
    except (FileNotFoundError, StoryStoreError):
        return None

    pages = payload["pages"]
    slots = 0
    alternatives = 0
    for page in pages:
        images = page.get("images", {})
        for slot_name in SLOT_NAMES:
            if slot_name not in images:
                continue
            slots += 1
            alternatives += len(images[slot_name].get("alternatives", []))

    story_rel = _normalize_rel_path(story_rel_path)
    return {
        "story_rel_path": story_rel,
        "story_id": payload["story_id"],
        "title": payload["title"],
        "status": payload["status"],
        "book_rel_path": payload["book_rel_path"],
        "schema_version": payload["schema_version"],
        "updated_at": payload["updated_at"],
        "pages": len(pages),
        "slots": slots,
        "alternatives": alternatives,
    }


def list_story_pages(story_rel_path: str) -> list[dict[str, Any]]:
    payload = load_story(story_rel_path)
    rows: list[dict[str, Any]] = []
    for page in payload["pages"]:
        rows.append(
            {
                "page_number": int(page["page_number"]),
                "status": str(page.get("status", "draft")),
                "text_original": str(page.get("text", {}).get("original", "")),
                "text_current": str(page.get("text", {}).get("current", "")),
            }
        )
    rows.sort(key=lambda item: item["page_number"])
    return rows


def _find_page(payload: dict[str, Any], page_number: int) -> dict[str, Any] | None:
    for page in payload.get("pages", []):
        if int(page.get("page_number", 0)) == int(page_number):
            return page
    return None


def _build_slot_view(slot_name: str, slot_payload: dict[str, Any]) -> dict[str, Any]:
    active_id = str(slot_payload.get("active_id", ""))
    alternatives = list(slot_payload.get("alternatives", []))
    active = next((item for item in alternatives if str(item.get("id")) == active_id), None)

    return {
        "slot_name": slot_name,
        "status": str(slot_payload.get("status", "draft")),
        "prompt_original": str(slot_payload.get("prompt", {}).get("original", "")),
        "prompt_current": str(slot_payload.get("prompt", {}).get("current", "")),
        "active_id": active_id,
        "active": active,
        "alternatives": alternatives,
    }


def get_story_page(story_rel_path: str, page_number: int) -> dict[str, Any] | None:
    payload = load_story(story_rel_path)
    page = _find_page(payload, page_number)
    if not page:
        return None

    return {
        "page_number": int(page["page_number"]),
        "status": str(page.get("status", "draft")),
        "text_original": str(page.get("text", {}).get("original", "")),
        "text_current": str(page.get("text", {}).get("current", "")),
        "images": page.get("images", {}),
    }


def list_page_slots(story_rel_path: str, page_number: int) -> list[dict[str, Any]]:
    payload = load_story(story_rel_path)
    page = _find_page(payload, page_number)
    if not page:
        return []

    images = page.get("images", {})
    items: list[dict[str, Any]] = []
    for slot_name in SLOT_NAMES:
        if slot_name not in images:
            continue
        items.append(_build_slot_view(slot_name, images[slot_name]))
    return items


def _ensure_slot(page: dict[str, Any], slot_name: str) -> dict[str, Any]:
    slot_name = _normalize_slot_name(slot_name)
    images = page.setdefault("images", {})
    if slot_name not in images or not isinstance(images[slot_name], dict):
        images[slot_name] = _slot_default(slot_name)
    return images[slot_name]


def save_page_edits(
    *,
    story_rel_path: str,
    page_number: int,
    text_current: str,
    main_prompt_current: str,
    secondary_prompt_current: str | None,
) -> dict[str, Any]:
    story_file = story_rel_to_json_path(story_rel_path)
    payload = _read_story_file(story_file)

    page = _find_page(payload, page_number)
    if not page:
        raise StoryStoreError(f"No existe pagina {page_number} en {story_rel_path}.")

    text_block = page.setdefault("text", {"original": "", "current": ""})
    text_block["current"] = str(text_current)

    main_slot = _ensure_slot(page, "main")
    main_slot.setdefault("prompt", {"original": "", "current": ""})
    main_slot["prompt"]["current"] = str(main_prompt_current)

    secondary_value = (secondary_prompt_current or "").strip()
    has_secondary = "secondary" in page.get("images", {})
    if secondary_value or has_secondary:
        secondary_slot = _ensure_slot(page, "secondary")
        secondary_slot.setdefault("prompt", {"original": "", "current": ""})
        secondary_slot["prompt"]["current"] = str(secondary_prompt_current or "")

    page["status"] = "draft"
    payload["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, payload)

    updated_page = get_story_page(story_rel_path, page_number)
    if not updated_page:
        raise StoryStoreError("No se pudo recargar la pagina tras guardar.")
    return updated_page


def _extension_for_mime(mime_type: str) -> str:
    lookup = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
        "image/gif": "gif",
    }
    return lookup.get(mime_type.lower(), "png")


def add_slot_alternative(
    *,
    story_rel_path: str,
    page_number: int,
    slot_name: str,
    image_bytes: bytes,
    mime_type: str,
    slug: str,
    notes: str,
) -> dict[str, Any]:
    if not image_bytes:
        raise StoryStoreError("No se recibieron bytes de imagen.")

    normalized_slot = _normalize_slot_name(slot_name)
    story_file = story_rel_to_json_path(story_rel_path)
    payload = _read_story_file(story_file)

    page = _find_page(payload, page_number)
    if not page:
        raise StoryStoreError(f"No existe pagina {page_number} en {story_rel_path}.")

    slot = _ensure_slot(page, normalized_slot)

    alt_id = uuid.uuid4().hex
    safe_slug = _normalize_slug(slug, normalized_slot)
    extension = _extension_for_mime(mime_type)

    file_name = f"img_{alt_id}_{safe_slug}.{extension}"
    book_dir = story_file.parent
    file_path = book_dir / file_name
    try:
        file_path.write_bytes(image_bytes)
    except OSError as exc:
        raise StoryStoreError(f"No se pudo guardar alternativa de imagen: {exc}") from exc

    book_rel = payload.get("book_rel_path", "")
    asset_rel_path = f"library/{book_rel}/{file_name}" if book_rel else f"library/{file_name}"
    asset_rel_path = asset_rel_path.replace("\\", "/")

    alternative = {
        "id": alt_id,
        "slug": safe_slug,
        "asset_rel_path": asset_rel_path,
        "mime_type": mime_type or "image/png",
        "status": "candidate",
        "created_at": _utc_now_iso(),
        "notes": notes.strip(),
    }

    alternatives = slot.setdefault("alternatives", [])
    alternatives.append(alternative)
    if not str(slot.get("active_id", "")).strip():
        slot["active_id"] = alt_id

    slot["status"] = "draft"
    page["status"] = "draft"
    payload["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, payload)

    return alternative


def set_slot_active(
    *,
    story_rel_path: str,
    page_number: int,
    slot_name: str,
    alternative_id: str,
) -> dict[str, Any]:
    normalized_slot = _normalize_slot_name(slot_name)
    story_file = story_rel_to_json_path(story_rel_path)
    payload = _read_story_file(story_file)

    page = _find_page(payload, page_number)
    if not page:
        raise StoryStoreError(f"No existe pagina {page_number} en {story_rel_path}.")

    slot = _ensure_slot(page, normalized_slot)
    alternatives = slot.get("alternatives", [])

    target = next((item for item in alternatives if str(item.get("id", "")) == alternative_id), None)
    if not target:
        raise StoryStoreError("La alternativa indicada no existe para este slot.")

    slot["active_id"] = alternative_id
    slot["status"] = "draft"
    page["status"] = "draft"
    payload["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, payload)

    return target


def resolve_media_rel_path(rel_path: str) -> Path:
    normalized = rel_path.strip().replace("\\", "/")
    target = (ROOT_DIR / normalized).resolve()

    root_abs = ROOT_DIR.resolve()
    if root_abs not in target.parents and target != root_abs:
        raise StoryStoreError("Ruta fuera del proyecto.")

    return target
