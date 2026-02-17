from __future__ import annotations

import json
import mimetypes
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT, ROOT_DIR

STORY_JSON_RE = re.compile(r"^(\d{2})\.json$", re.IGNORECASE)
SLOT_NAMES = ("main", "secondary")
STORY_STATUS_VALUES = {"draft", "in_review", "definitive"}


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
    return value or fallback


def _coerce_string_list(raw_value: Any) -> list[str]:
    if not isinstance(raw_value, list):
        return []

    values: list[str] = []
    seen: set[str] = set()
    for item in raw_value:
        text = str(item).strip()
        if not text or text in seen:
            continue
        values.append(text)
        seen.add(text)
    return values


def _slot_default() -> dict[str, Any]:
    return {
        "status": "draft",
        "prompt": "",
        "reference_ids": [],
        "active_id": "",
        "alternatives": [],
    }


def _slot_has_content(slot: dict[str, Any]) -> bool:
    return bool(
        str(slot.get("prompt", "")).strip()
        or slot.get("reference_ids")
        or slot.get("alternatives")
        or str(slot.get("active_id", "")).strip()
    )


def _guess_mime_type(file_name: str) -> str:
    guess = mimetypes.guess_type(file_name)[0]
    return guess or "image/png"


def _coerce_alternative(raw_value: Any) -> dict[str, Any] | None:
    if not isinstance(raw_value, dict):
        return None

    alt_id = str(raw_value.get("id", "")).strip()
    if not alt_id:
        return None

    asset_rel_path = str(raw_value.get("asset_rel_path", "")).strip().replace("\\", "/")
    mime_type = str(raw_value.get("mime_type", "")).strip() or _guess_mime_type(alt_id)
    slug = str(raw_value.get("slug", "")).strip()
    if not slug:
        stem = Path(alt_id).stem
        slug = _normalize_slug(stem, "image")

    return {
        "id": alt_id,
        "slug": slug,
        "asset_rel_path": asset_rel_path,
        "mime_type": mime_type,
        "status": str(raw_value.get("status", "")).strip() or "candidate",
        "created_at": str(raw_value.get("created_at", "")).strip() or _utc_now_iso(),
        "notes": str(raw_value.get("notes", "")).strip(),
    }


def _coerce_slot(raw_value: Any) -> dict[str, Any]:
    base = _slot_default()
    if not isinstance(raw_value, dict):
        return base

    prompt = raw_value.get("prompt", "")
    base["prompt"] = str(prompt).strip() if isinstance(prompt, str) else ""

    status = str(raw_value.get("status", "")).strip()
    if status:
        base["status"] = status

    base["reference_ids"] = _coerce_string_list(raw_value.get("reference_ids", []))

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

    text = raw_value.get("text", "")
    text_value = str(text) if isinstance(text, str) else ""

    images_raw = raw_value.get("images", {})
    if not isinstance(images_raw, dict):
        images_raw = {}

    main_slot = _coerce_slot(images_raw.get("main", {}))

    page: dict[str, Any] = {
        "page_number": page_number,
        "text": text_value,
        "images": {
            "main": main_slot,
        },
    }

    secondary_slot = _coerce_slot(images_raw.get("secondary", {}))
    if "secondary" in images_raw or _slot_has_content(secondary_slot):
        page["images"]["secondary"] = secondary_slot

    return page


def _coerce_story_payload(payload: Any, *, story_id_hint: str, book_rel_path_hint: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StoryStoreError("El contenido del cuento debe ser un objeto JSON.")

    story_id = str(payload.get("story_id", "")).strip() or story_id_hint
    if not re.fullmatch(r"\d{2}", story_id):
        if re.fullmatch(r"\d{2}", story_id_hint):
            story_id = story_id_hint
        else:
            raise StoryStoreError("story_id invalido en JSON.")

    title = str(payload.get("title", "")).strip() or f"Cuento {story_id}"
    status = str(payload.get("status", "")).strip() or "draft"
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
    cover = _coerce_slot(payload.get("cover", {}))

    return {
        "story_id": story_id,
        "title": title,
        "status": status,
        "book_rel_path": book_rel_path,
        "created_at": created_at,
        "updated_at": updated_at,
        "cover": cover,
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
            slot = images.get(slot_name)
            if not isinstance(slot, dict):
                continue
            slots += 1
            alternatives += len(slot.get("alternatives", []))

    cover_alternatives = len(payload.get("cover", {}).get("alternatives", []))

    story_rel = _normalize_rel_path(story_rel_path)
    return {
        "story_rel_path": story_rel,
        "story_id": payload["story_id"],
        "title": payload["title"],
        "status": payload["status"],
        "book_rel_path": payload["book_rel_path"],
        "created_at": payload["created_at"],
        "updated_at": payload["updated_at"],
        "pages": len(pages),
        "slots": slots,
        "alternatives": alternatives,
        "cover_alternatives": cover_alternatives,
    }


def list_story_pages(story_rel_path: str) -> list[dict[str, Any]]:
    payload = load_story(story_rel_path)
    rows: list[dict[str, Any]] = []
    for page in payload["pages"]:
        rows.append(
            {
                "page_number": int(page["page_number"]),
                "text": str(page.get("text", "")),
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
        "prompt": str(slot_payload.get("prompt", "")),
        "reference_ids": _coerce_string_list(slot_payload.get("reference_ids", [])),
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
        "text": str(page.get("text", "")),
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
        slot = images.get(slot_name)
        if not isinstance(slot, dict):
            continue
        items.append(_build_slot_view(slot_name, slot))
    return items


def get_story_cover(story_rel_path: str) -> dict[str, Any]:
    payload = load_story(story_rel_path)
    cover = payload.get("cover", _slot_default())
    return _build_slot_view("cover", cover)

def _ensure_slot(page: dict[str, Any], slot_name: str) -> dict[str, Any]:
    slot_name = _normalize_slot_name(slot_name)
    images = page.setdefault("images", {})
    if slot_name not in images or not isinstance(images[slot_name], dict):
        images[slot_name] = _slot_default()
    return images[slot_name]


def _ensure_cover(payload: dict[str, Any]) -> dict[str, Any]:
    cover = payload.get("cover")
    if not isinstance(cover, dict):
        cover = _slot_default()
        payload["cover"] = cover
    return cover


def _parse_reference_ids(raw_value: str | None) -> list[str]:
    if raw_value is None:
        return []

    parts = [item.strip() for item in str(raw_value).split(",")]
    values: list[str] = []
    seen: set[str] = set()
    for part in parts:
        if not part:
            continue
        if part in seen:
            continue
        values.append(part)
        seen.add(part)
    return values


def save_page_edits(
    *,
    story_rel_path: str,
    page_number: int,
    text: str,
    main_prompt: str,
    secondary_prompt: str | None,
    main_reference_ids: str | None,
    secondary_reference_ids: str | None,
) -> dict[str, Any]:
    story_file = story_rel_to_json_path(story_rel_path)
    payload = _read_story_file(story_file)

    page = _find_page(payload, page_number)
    if not page:
        raise StoryStoreError(f"No existe pagina {page_number} en {story_rel_path}.")

    page["text"] = str(text)

    main_slot = _ensure_slot(page, "main")
    main_slot["prompt"] = str(main_prompt)
    main_slot["reference_ids"] = _parse_reference_ids(main_reference_ids)

    secondary_value = (secondary_prompt or "").strip()
    secondary_refs = _parse_reference_ids(secondary_reference_ids)
    has_secondary = "secondary" in page.get("images", {})
    if secondary_value or secondary_refs or has_secondary:
        secondary_slot = _ensure_slot(page, "secondary")
        secondary_slot["prompt"] = str(secondary_prompt or "")
        secondary_slot["reference_ids"] = secondary_refs

    payload["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, payload)

    updated_page = get_story_page(story_rel_path, page_number)
    if not updated_page:
        raise StoryStoreError("No se pudo recargar la pagina tras guardar.")
    return updated_page


def save_cover_edits(*, story_rel_path: str, prompt: str, reference_ids: str | None) -> dict[str, Any]:
    story_file = story_rel_to_json_path(story_rel_path)
    payload = _read_story_file(story_file)

    cover = _ensure_cover(payload)
    cover["prompt"] = str(prompt)
    cover["reference_ids"] = _parse_reference_ids(reference_ids)

    payload["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, payload)
    return get_story_cover(story_rel_path)


def _extension_for_mime(mime_type: str) -> str:
    lookup = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
        "image/gif": "gif",
    }
    return lookup.get(mime_type.lower(), "png")


def _node_images_dir(node_rel_path: str) -> Path:
    normalized = _normalize_rel_path(node_rel_path)
    if normalized:
        return LIBRARY_ROOT / normalized / "images"
    return LIBRARY_ROOT / "images"


def _asset_rel_path_for_node(node_rel_path: str, file_name: str) -> str:
    normalized = _normalize_rel_path(node_rel_path)
    if normalized:
        return f"library/{normalized}/images/{file_name}"
    return f"library/images/{file_name}"


def _image_index_path(node_rel_path: str) -> Path:
    return _node_images_dir(node_rel_path) / "index.json"


def _load_image_index(node_rel_path: str) -> list[dict[str, Any]]:
    index_path = _image_index_path(node_rel_path)
    if not index_path.exists() or not index_path.is_file():
        return []

    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(payload, list):
        return []

    entries: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        file_name = str(item.get("filename", "")).strip()
        if not file_name:
            continue
        entries.append(
            {
                "filename": file_name,
                "asset_rel_path": str(item.get("asset_rel_path", "")).strip().replace("\\", "/"),
                "description": str(item.get("description", "")).strip(),
                "node_rel_path": _normalize_rel_path(str(item.get("node_rel_path", ""))),
                "created_at": str(item.get("created_at", "")).strip() or _utc_now_iso(),
            }
        )
    return entries


def _write_image_index(node_rel_path: str, entries: list[dict[str, Any]]) -> None:
    index_path = _image_index_path(node_rel_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    try:
        index_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise StoryStoreError(f"No se pudo escribir index de imagenes: {exc}") from exc


def _upsert_image_index(*, node_rel_path: str, file_name: str, description: str) -> None:
    entries = _load_image_index(node_rel_path)
    asset_rel_path = _asset_rel_path_for_node(node_rel_path, file_name)
    normalized_node = _normalize_rel_path(node_rel_path)

    updated = False
    for item in entries:
        if item["filename"] != file_name:
            continue
        item["asset_rel_path"] = asset_rel_path
        item["description"] = description.strip()
        item["node_rel_path"] = normalized_node
        updated = True
        break

    if not updated:
        entries.append(
            {
                "filename": file_name,
                "asset_rel_path": asset_rel_path,
                "description": description.strip(),
                "node_rel_path": normalized_node,
                "created_at": _utc_now_iso(),
            }
        )

    entries.sort(key=lambda item: item["filename"].lower())
    _write_image_index(node_rel_path, entries)


def _write_node_image(*, node_rel_path: str, file_name: str, image_bytes: bytes) -> Path:
    images_dir = _node_images_dir(node_rel_path)
    images_dir.mkdir(parents=True, exist_ok=True)
    file_path = images_dir / file_name
    try:
        file_path.write_bytes(image_bytes)
    except OSError as exc:
        raise StoryStoreError(f"No se pudo guardar alternativa de imagen: {exc}") from exc
    return file_path


def _new_alternative(*, node_rel_path: str, slug: str, mime_type: str, notes: str) -> dict[str, Any]:
    extension = _extension_for_mime(mime_type)
    safe_slug = _normalize_slug(slug, "image")
    file_name = f"{uuid.uuid4().hex}_{safe_slug}.{extension}"
    asset_rel_path = _asset_rel_path_for_node(node_rel_path, file_name)
    return {
        "id": file_name,
        "slug": safe_slug,
        "asset_rel_path": asset_rel_path,
        "mime_type": mime_type or "image/png",
        "status": "candidate",
        "created_at": _utc_now_iso(),
        "notes": notes.strip(),
    }


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
    node_rel_path = _normalize_rel_path(str(payload.get("book_rel_path", "")))
    safe_slug = _normalize_slug(slug, normalized_slot)

    alternative = _new_alternative(node_rel_path=node_rel_path, slug=safe_slug, mime_type=mime_type, notes=notes)
    _write_node_image(node_rel_path=node_rel_path, file_name=alternative["id"], image_bytes=image_bytes)
    _upsert_image_index(
        node_rel_path=node_rel_path,
        file_name=alternative["id"],
        description=f"story {payload['story_id']} page {page_number} slot {normalized_slot}",
    )

    alternatives = slot.setdefault("alternatives", [])
    alternatives.append(alternative)
    if not str(slot.get("active_id", "")).strip():
        slot["active_id"] = alternative["id"]

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
    payload["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, payload)
    return target


def add_cover_alternative(
    *,
    story_rel_path: str,
    image_bytes: bytes,
    mime_type: str,
    slug: str,
    notes: str,
) -> dict[str, Any]:
    if not image_bytes:
        raise StoryStoreError("No se recibieron bytes de imagen.")

    story_file = story_rel_to_json_path(story_rel_path)
    payload = _read_story_file(story_file)
    cover = _ensure_cover(payload)

    node_rel_path = _normalize_rel_path(str(payload.get("book_rel_path", "")))
    safe_slug = _normalize_slug(slug, "cover")
    alternative = _new_alternative(node_rel_path=node_rel_path, slug=safe_slug, mime_type=mime_type, notes=notes)

    _write_node_image(node_rel_path=node_rel_path, file_name=alternative["id"], image_bytes=image_bytes)
    _upsert_image_index(
        node_rel_path=node_rel_path,
        file_name=alternative["id"],
        description=f"story {payload['story_id']} cover",
    )

    alternatives = cover.setdefault("alternatives", [])
    alternatives.append(alternative)
    if not str(cover.get("active_id", "")).strip():
        cover["active_id"] = alternative["id"]

    payload["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, payload)
    return alternative


def set_cover_active(*, story_rel_path: str, alternative_id: str) -> dict[str, Any]:
    story_file = story_rel_to_json_path(story_rel_path)
    payload = _read_story_file(story_file)
    cover = _ensure_cover(payload)

    alternatives = cover.get("alternatives", [])
    target = next((item for item in alternatives if str(item.get("id", "")) == alternative_id), None)
    if not target:
        raise StoryStoreError("La alternativa indicada no existe para la portada.")

    cover["active_id"] = alternative_id
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


def _node_levels(node_rel_path: str) -> list[str]:
    normalized = _normalize_rel_path(node_rel_path)
    if not normalized:
        return [""]

    parts = [item for item in normalized.split("/") if item]
    levels = [""]
    current: list[str] = []
    for part in parts:
        current.append(part)
        levels.append("/".join(current))
    return levels


def resolve_reference_assets(node_rel_path: str, reference_ids: list[str]) -> list[dict[str, Any]]:
    normalized_node = _normalize_rel_path(node_rel_path)
    search_levels = list(reversed(_node_levels(normalized_node)))

    items: list[dict[str, Any]] = []
    for raw_name in reference_ids:
        file_name = Path(str(raw_name).strip()).name
        if not file_name:
            continue

        found_rel_path = ""
        found_node = ""
        for level in search_levels:
            candidate = _node_images_dir(level) / file_name
            if candidate.exists() and candidate.is_file():
                found_rel_path = _asset_rel_path_for_node(level, file_name)
                found_node = level
                break

        items.append(
            {
                "filename": file_name,
                "found": bool(found_rel_path),
                "asset_rel_path": found_rel_path,
                "node_rel_path": found_node,
            }
        )

    return items


def save_story_payload(
    *,
    story_rel_path: str,
    payload: dict[str, Any],
    touch_updated_at: bool = True,
) -> dict[str, Any]:
    story_file = story_rel_to_json_path(story_rel_path)
    story_id_hint = story_file.stem
    book_rel_hint = (
        story_file.parent.resolve().relative_to(LIBRARY_ROOT.resolve()).as_posix()
        if story_file.parent.resolve() != LIBRARY_ROOT.resolve()
        else ""
    )
    normalized = _coerce_story_payload(payload, story_id_hint=story_id_hint, book_rel_path_hint=book_rel_hint)
    if touch_updated_at:
        normalized["updated_at"] = _utc_now_iso()
    _write_story_file(story_file, normalized)
    return normalized


def set_story_status(*, story_rel_path: str, status: str) -> dict[str, Any]:
    normalized_status = status.strip().lower()
    if normalized_status not in STORY_STATUS_VALUES:
        raise StoryStoreError(f"status invalido: {status}")

    payload = load_story(story_rel_path)
    payload["status"] = normalized_status
    return save_story_payload(story_rel_path=story_rel_path, payload=payload, touch_updated_at=True)

def meta_path_for_node(node_rel_path: str) -> Path:
    normalized = _normalize_rel_path(node_rel_path)
    if normalized:
        return LIBRARY_ROOT / normalized / "meta.json"
    return LIBRARY_ROOT / "meta.json"


def _default_meta(node_rel_path: str) -> dict[str, Any]:
    normalized = _normalize_rel_path(node_rel_path)
    title = normalized.split("/")[-1] if normalized else "Biblioteca"
    return {
        "collection": {
            "title": title,
        },
        "anchors": [],
        "updated_at": _utc_now_iso(),
    }


def _coerce_anchor(raw_value: Any) -> dict[str, Any] | None:
    if not isinstance(raw_value, dict):
        return None

    anchor_id = str(raw_value.get("id", "")).strip()
    if not anchor_id:
        return None

    name = str(raw_value.get("name", "")).strip() or anchor_id
    prompt = raw_value.get("prompt", "")
    prompt_text = str(prompt).strip() if isinstance(prompt, str) else ""
    image_filenames = _coerce_string_list(raw_value.get("image_filenames", []))

    alternatives: list[dict[str, Any]] = []
    for item in raw_value.get("alternatives", []):
        alt = _coerce_alternative(item)
        if alt:
            alternatives.append(alt)

    for alt in alternatives:
        alt_id = str(alt.get("id", "")).strip()
        if alt_id and alt_id not in image_filenames:
            image_filenames.append(alt_id)

    active_id = str(raw_value.get("active_id", "")).strip()
    if active_id and not any(item["id"] == active_id for item in alternatives):
        active_id = ""
    if not active_id and alternatives:
        active_id = alternatives[0]["id"]

    anchor: dict[str, Any] = {
        "id": anchor_id,
        "name": name,
        "prompt": prompt_text,
        "image_filenames": image_filenames,
        "status": str(raw_value.get("status", "")).strip() or "draft",
        "active_id": active_id,
        "alternatives": alternatives,
    }
    return anchor


def _coerce_meta_payload(payload: Any, node_rel_path: str) -> dict[str, Any]:
    base = _default_meta(node_rel_path)
    if not isinstance(payload, dict):
        return base

    collection = payload.get("collection", {})
    if isinstance(collection, dict):
        title = str(collection.get("title", "")).strip()
        if title:
            base["collection"]["title"] = title

    anchors: list[dict[str, Any]] = []
    for item in payload.get("anchors", []):
        anchor = _coerce_anchor(item)
        if anchor:
            anchors.append(anchor)
    base["anchors"] = anchors

    updated_at = str(payload.get("updated_at", "")).strip()
    if updated_at:
        base["updated_at"] = updated_at

    if "style_rules" in payload:
        base["style_rules"] = payload["style_rules"]
    if "continuity_rules" in payload:
        base["continuity_rules"] = payload["continuity_rules"]

    return base


def load_node_meta(node_rel_path: str, *, create_if_missing: bool = False) -> dict[str, Any]:
    normalized_node = _normalize_rel_path(node_rel_path)
    meta_path = meta_path_for_node(normalized_node)

    if not meta_path.exists() or not meta_path.is_file():
        if not create_if_missing:
            raise FileNotFoundError(f"No existe meta.json en {normalized_node or 'library'}")
        payload = _default_meta(normalized_node)
        save_node_meta(normalized_node, payload, touch_updated_at=True)
        return payload

    try:
        raw_payload = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StoryStoreError(f"JSON invalido en {meta_path}: {exc}") from exc

    return _coerce_meta_payload(raw_payload, normalized_node)


def get_node_meta(node_rel_path: str) -> dict[str, Any] | None:
    try:
        return load_node_meta(node_rel_path, create_if_missing=False)
    except (FileNotFoundError, StoryStoreError):
        return None


def save_node_meta(node_rel_path: str, payload: dict[str, Any], *, touch_updated_at: bool = True) -> dict[str, Any]:
    normalized_node = _normalize_rel_path(node_rel_path)
    normalized = _coerce_meta_payload(payload, normalized_node)
    if touch_updated_at:
        normalized["updated_at"] = _utc_now_iso()

    meta_path = meta_path_for_node(normalized_node)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(normalized, indent=2, ensure_ascii=False) + "\n"

    try:
        meta_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise StoryStoreError(f"No se pudo guardar meta.json: {exc}") from exc

    return normalized


def list_meta_hierarchy(node_rel_path: str) -> list[dict[str, Any]]:
    normalized_node = _normalize_rel_path(node_rel_path)
    rows: list[dict[str, Any]] = []

    for level in _node_levels(normalized_node):
        meta = get_node_meta(level)
        if not meta:
            continue
        rows.append(
            {
                "node_rel_path": level,
                "meta": meta,
            }
        )

    return rows


def list_applicable_anchors(node_rel_path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in list_meta_hierarchy(node_rel_path):
        level = item["node_rel_path"]
        meta = item["meta"]
        for anchor in meta.get("anchors", []):
            if not isinstance(anchor, dict):
                continue
            anchor_row = dict(anchor)
            anchor_row["source_node_rel_path"] = level
            rows.append(anchor_row)

    rows.sort(key=lambda item: (str(item.get("name", "")).lower(), str(item.get("id", "")).lower()))
    return rows


def upsert_anchor(*, node_rel_path: str, anchor_id: str, name: str, prompt: str, status: str) -> dict[str, Any]:
    normalized_node = _normalize_rel_path(node_rel_path)
    if not anchor_id.strip():
        raise StoryStoreError("anchor_id es obligatorio.")

    meta = load_node_meta(normalized_node, create_if_missing=True)
    anchors = meta.setdefault("anchors", [])

    existing = next((item for item in anchors if str(item.get("id", "")) == anchor_id), None)
    if existing is None:
        existing = {
            "id": anchor_id,
            "name": name.strip() or anchor_id,
            "prompt": prompt.strip(),
            "image_filenames": [],
            "status": status.strip() or "draft",
            "active_id": "",
            "alternatives": [],
        }
        anchors.append(existing)
    else:
        existing["name"] = name.strip() or anchor_id
        existing["prompt"] = prompt.strip()
        existing["status"] = status.strip() or str(existing.get("status", "draft"))

    save_node_meta(normalized_node, meta, touch_updated_at=True)
    return existing


def _find_anchor(meta: dict[str, Any], anchor_id: str) -> dict[str, Any] | None:
    for anchor in meta.get("anchors", []):
        if str(anchor.get("id", "")) == anchor_id:
            return anchor
    return None


def add_anchor_alternative(
    *,
    node_rel_path: str,
    anchor_id: str,
    image_bytes: bytes,
    mime_type: str,
    slug: str,
    notes: str,
) -> dict[str, Any]:
    if not image_bytes:
        raise StoryStoreError("No se recibieron bytes de imagen.")

    normalized_node = _normalize_rel_path(node_rel_path)
    meta = load_node_meta(normalized_node, create_if_missing=True)
    anchor = _find_anchor(meta, anchor_id)
    if not anchor:
        raise StoryStoreError(f"No existe anchor_id {anchor_id} en {normalized_node or 'library'}.")

    safe_slug = _normalize_slug(slug, _normalize_slug(anchor_id, "anchor"))
    alternative = _new_alternative(node_rel_path=normalized_node, slug=safe_slug, mime_type=mime_type, notes=notes)

    _write_node_image(node_rel_path=normalized_node, file_name=alternative["id"], image_bytes=image_bytes)
    _upsert_image_index(
        node_rel_path=normalized_node,
        file_name=alternative["id"],
        description=f"anchor {anchor_id}",
    )

    alternatives = anchor.setdefault("alternatives", [])
    alternatives.append(alternative)

    image_filenames = anchor.setdefault("image_filenames", [])
    if alternative["id"] not in image_filenames:
        image_filenames.append(alternative["id"])

    if not str(anchor.get("active_id", "")).strip():
        anchor["active_id"] = alternative["id"]

    save_node_meta(normalized_node, meta, touch_updated_at=True)
    return alternative


def set_anchor_active(*, node_rel_path: str, anchor_id: str, alternative_id: str) -> dict[str, Any]:
    normalized_node = _normalize_rel_path(node_rel_path)
    meta = load_node_meta(normalized_node, create_if_missing=False)
    anchor = _find_anchor(meta, anchor_id)
    if not anchor:
        raise StoryStoreError(f"No existe anchor_id {anchor_id} en {normalized_node or 'library'}.")

    alternatives = anchor.get("alternatives", [])
    target = next((item for item in alternatives if str(item.get("id", "")) == alternative_id), None)
    if not target:
        raise StoryStoreError("La alternativa indicada no existe para esta ancla.")

    anchor["active_id"] = alternative_id
    image_filenames = anchor.setdefault("image_filenames", [])
    if alternative_id not in image_filenames:
        image_filenames.append(alternative_id)

    save_node_meta(normalized_node, meta, touch_updated_at=True)
    return target


def list_node_levels(node_rel_path: str) -> list[str]:
    return _node_levels(node_rel_path)
