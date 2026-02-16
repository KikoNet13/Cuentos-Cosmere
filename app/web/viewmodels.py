from __future__ import annotations

from typing import Any

from flask import url_for

from ..catalog_provider import get_story_summary
from ..story_store import StoryStoreError, get_story_page, list_page_slots, list_story_pages, resolve_media_rel_path
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

    slot_map = {item["slot_name"]: item for item in slot_items}
    main_slot = slot_map.get("main")
    secondary_slot = slot_map.get("secondary")

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

    return {
        "story": story,
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
        "read_main_image": _resolve_slot_image(main_slot),
        "read_secondary_image": _resolve_slot_image(secondary_slot),
        "breadcrumbs": build_breadcrumbs(normalized),
        "editor_mode": editor_mode,
    }

