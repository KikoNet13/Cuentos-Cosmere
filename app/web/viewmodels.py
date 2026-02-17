from __future__ import annotations

from typing import Any

from flask import url_for

from ..catalog_provider import get_story_summary
from ..story_store import (
    StoryStoreError,
    get_story_cover,
    get_story_page,
    list_applicable_anchors,
    list_meta_hierarchy,
    list_node_levels,
    list_page_slots,
    list_story_pages,
    resolve_media_rel_path,
    resolve_reference_assets,
)
from .common import build_breadcrumbs, normalize_rel_path


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

    alt_id = str(alternative.get("id", ""))
    return {
        "id": alt_id,
        "slug": str(alternative.get("slug", "")),
        "asset_rel_path": rel_path,
        "mime_type": str(alternative.get("mime_type", "")),
        "status": str(alternative.get("status", "candidate")),
        "created_at": str(alternative.get("created_at", "")),
        "notes": str(alternative.get("notes", "")),
        "is_active": alt_id == active_id,
        "image_exists": image_exists,
        "image_url": image_url,
    }


def _build_reference_views(book_rel_path: str, reference_ids: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ref in resolve_reference_assets(book_rel_path, reference_ids):
        row = dict(ref)
        row["image_url"] = (
            url_for("web.media_file", rel_path=row["asset_rel_path"])
            if row.get("found") and row.get("asset_rel_path")
            else ""
        )
        rows.append(row)
    return rows


def _build_slot_item(raw_slot: dict[str, Any], book_rel_path: str) -> dict[str, Any]:
    active_id = str(raw_slot.get("active_id", ""))
    alternatives = [_build_alternative_view(item, active_id) for item in raw_slot.get("alternatives", [])]
    active_item = next((item for item in alternatives if item["is_active"]), None)
    reference_ids = list(raw_slot.get("reference_ids", []))

    return {
        "slot_name": str(raw_slot.get("slot_name", "main")),
        "status": str(raw_slot.get("status", "draft")),
        "prompt": str(raw_slot.get("prompt", "")),
        "reference_ids": reference_ids,
        "reference_ids_csv": ", ".join(reference_ids),
        "reference_assets": _build_reference_views(book_rel_path, reference_ids),
        "active_id": active_id,
        "active_item": active_item,
        "alternatives": alternatives,
    }


def _resolve_slot_image(slot_item: dict[str, Any] | None) -> dict[str, Any] | None:
    if not slot_item:
        return None

    active_item = slot_item.get("active_item")
    if isinstance(active_item, dict) and active_item.get("image_exists"):
        return active_item

    for alternative in slot_item.get("alternatives", []):
        if alternative.get("image_exists"):
            return alternative

    return None


def _level_label(level: str) -> str:
    if not level:
        return "global (library)"
    return level


def _build_anchor_view(anchor: dict[str, Any], book_rel_path: str) -> dict[str, Any]:
    active_id = str(anchor.get("active_id", ""))
    alternatives = [_build_alternative_view(item, active_id) for item in anchor.get("alternatives", [])]
    active_item = next((item for item in alternatives if item["is_active"]), None)
    image_filenames = [str(item).strip() for item in anchor.get("image_filenames", []) if str(item).strip()]

    return {
        "id": str(anchor.get("id", "")),
        "name": str(anchor.get("name", "")),
        "prompt": str(anchor.get("prompt", "")),
        "status": str(anchor.get("status", "draft")),
        "source_node_rel_path": str(anchor.get("source_node_rel_path", "")),
        "source_label": _level_label(str(anchor.get("source_node_rel_path", ""))),
        "image_filenames": image_filenames,
        "image_filenames_csv": ", ".join(image_filenames),
        "reference_assets": _build_reference_views(book_rel_path, image_filenames),
        "active_id": active_id,
        "active_item": active_item,
        "alternatives": alternatives,
    }


def build_story_view_model(
    story_rel_path: str,
    selected_page_number: int,
    *,
    editor_mode: bool,
) -> dict[str, Any] | None:
    normalized = normalize_rel_path(story_rel_path)
    story = get_story_summary(normalized)
    if not story:
        return None

    book_rel_path = str(story.get("book_rel_path", ""))
    pages = list_story_pages(normalized)
    page_numbers = [int(page["page_number"]) for page in pages]
    default_page_number = page_numbers[0] if page_numbers else 1

    selected_page = selected_page_number if selected_page_number > 0 else default_page_number
    if page_numbers and selected_page not in page_numbers:
        selected_page = default_page_number

    page = get_story_page(normalized, selected_page) if page_numbers else None

    slot_items: list[dict[str, Any]] = []
    if page:
        for slot in list_page_slots(normalized, selected_page):
            slot_items.append(_build_slot_item(slot, book_rel_path))

    slot_map = {item["slot_name"]: item for item in slot_items}
    main_slot = slot_map.get("main")
    secondary_slot = slot_map.get("secondary")
    cover_slot = _build_slot_item(get_story_cover(normalized), book_rel_path)

    missing_pages: list[int] = []
    if page_numbers:
        max_page = max(page_numbers)
        present = set(page_numbers)
        missing_pages = [value for value in range(1, max_page + 1) if value not in present]

    prev_page = None
    next_page = None
    if page_numbers and selected_page in page_numbers:
        index = page_numbers.index(selected_page)
        prev_page = page_numbers[index - 1] if index > 0 else None
        next_page = page_numbers[index + 1] if index + 1 < len(page_numbers) else None

    meta_hierarchy = list_meta_hierarchy(book_rel_path)
    anchor_items = [_build_anchor_view(item, book_rel_path) for item in list_applicable_anchors(book_rel_path)]
    level_options = [{"path": level, "label": _level_label(level)} for level in list_node_levels(book_rel_path)]

    return {
        "story": story,
        "book_rel_path": book_rel_path,
        "page_numbers": page_numbers,
        "selected_page": selected_page,
        "page": page,
        "prev_page": prev_page,
        "next_page": next_page,
        "missing_pages": missing_pages,
        "slots": slot_items,
        "slot_map": slot_map,
        "main_slot": main_slot,
        "secondary_slot": secondary_slot,
        "cover_slot": cover_slot,
        "read_main_image": _resolve_slot_image(main_slot),
        "read_secondary_image": _resolve_slot_image(secondary_slot),
        "read_cover_image": _resolve_slot_image(cover_slot),
        "meta_hierarchy": meta_hierarchy,
        "anchors": anchor_items,
        "anchor_level_options": level_options,
        "breadcrumbs": build_breadcrumbs(normalized),
        "editor_mode": editor_mode,
    }
