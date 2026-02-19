from __future__ import annotations

from pathlib import Path
from typing import Any

from .story_store import StoryStoreError, resolve_media_rel_path

SLOT_STATE_COMPLETED = "completed"
SLOT_STATE_PENDING = "pending"
SLOT_STATE_NO_PROMPT = "no_prompt"
SLOT_STATE_NOT_REQUIRED = "not_required"


def coerce_string_list(raw_value: Any) -> list[str]:
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


def get_active_alternative(slot_payload: dict[str, Any]) -> dict[str, Any] | None:
    active_id = str(slot_payload.get("active_id", "")).strip()
    if not active_id:
        return None

    alternatives = slot_payload.get("alternatives", [])
    if not isinstance(alternatives, list):
        return None

    return next(
        (
            item
            for item in alternatives
            if isinstance(item, dict) and str(item.get("id", "")).strip() == active_id
        ),
        None,
    )


def resolve_active_asset_path(slot_payload: dict[str, Any]) -> Path | None:
    active = get_active_alternative(slot_payload)
    if not active:
        return None

    rel_path = str(active.get("asset_rel_path", "")).strip().replace("\\", "/")
    if not rel_path:
        return None

    try:
        return resolve_media_rel_path(rel_path)
    except StoryStoreError:
        return None


def has_valid_active_image(slot_payload: dict[str, Any]) -> bool:
    file_path = resolve_active_asset_path(slot_payload)
    if not file_path:
        return False
    return file_path.exists() and file_path.is_file()


def slot_state(slot_payload: dict[str, Any]) -> str:
    status = str(slot_payload.get("status", "")).strip().lower()
    if status == SLOT_STATE_NOT_REQUIRED:
        return SLOT_STATE_NOT_REQUIRED

    prompt = str(slot_payload.get("prompt", "")).strip()
    if not prompt:
        return SLOT_STATE_NO_PROMPT

    if has_valid_active_image(slot_payload):
        return SLOT_STATE_COMPLETED

    return SLOT_STATE_PENDING
