from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import g, has_request_context

from ..config import LIBRARY_ROOT
from ..story_store import (
    StoryStoreError,
    json_path_to_story_rel,
    list_story_json_files,
    load_story,
    resolve_media_rel_path,
    resolve_reference_assets,
)

EXCLUDED_TOP_LEVEL_DIRS = {"_inbox", "_processed", "_backups"}


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _read_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8-sig")
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _is_in_excluded_area(rel_path: str) -> bool:
    normalized = _normalize_rel_path(rel_path)
    if not normalized:
        return False
    parts = [part for part in normalized.split("/") if part and part != "."]
    if not parts:
        return False

    first = parts[0]
    if first in EXCLUDED_TOP_LEVEL_DIRS:
        return True

    return any(part.startswith("_") for part in parts)


def _has_valid_active_image(slot: dict[str, Any]) -> bool:
    active_id = str(slot.get("active_id", "")).strip()
    if not active_id:
        return False

    alternatives = slot.get("alternatives", [])
    if not isinstance(alternatives, list):
        return False

    target = next(
        (
            item
            for item in alternatives
            if isinstance(item, dict) and str(item.get("id", "")).strip() == active_id
        ),
        None,
    )
    if not target:
        return False

    rel_path = str(target.get("asset_rel_path", "")).strip().replace("\\", "/")
    if not rel_path:
        return False

    try:
        file_path = resolve_media_rel_path(rel_path)
    except StoryStoreError:
        return False
    return file_path.exists() and file_path.is_file()


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


def _slot_state(slot_payload: dict[str, Any]) -> str:
    status = str(slot_payload.get("status", "")).strip().lower()
    if status == "not_required":
        return "not_required"

    prompt = str(slot_payload.get("prompt", "")).strip()
    if not prompt:
        return "no_prompt"

    if _has_valid_active_image(slot_payload):
        return "completed"

    return "pending"


def _build_reference_assets(node_rel_path: str, reference_ids: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ref in resolve_reference_assets(node_rel_path, reference_ids):
        row = dict(ref)
        row["filename"] = str(row.get("filename", ""))
        row["asset_rel_path"] = str(row.get("asset_rel_path", ""))
        row["node_rel_path"] = str(row.get("node_rel_path", ""))
        row["found"] = bool(row.get("found"))
        rows.append(row)
    return rows


def _iter_story_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for story_file in list_story_json_files():
        try:
            story_rel_path = json_path_to_story_rel(story_file)
        except StoryStoreError:
            continue

        if _is_in_excluded_area(story_rel_path):
            continue

        try:
            payload = load_story(story_rel_path)
        except (FileNotFoundError, StoryStoreError):
            continue

        story_rel_path = _normalize_rel_path(story_rel_path)
        book_rel_path = _normalize_rel_path(str(payload.get("book_rel_path", "")))
        first_page = 1
        pages = payload.get("pages", [])
        if isinstance(pages, list) and pages:
            first = pages[0]
            if isinstance(first, dict):
                try:
                    first_page = max(1, int(first.get("page_number", 1)))
                except (TypeError, ValueError):
                    first_page = 1

        records.append(
            {
                "story_rel_path": story_rel_path,
                "story_id": str(payload.get("story_id", "")).strip(),
                "title": str(payload.get("title", "")).strip() or story_rel_path.split("/")[-1],
                "book_rel_path": book_rel_path,
                "first_page": first_page,
                "payload": payload,
            }
        )

    records.sort(key=lambda item: item["story_rel_path"])
    return records


def _pick_editor_story_for_anchor(node_rel_path: str, story_records: list[dict[str, Any]]) -> tuple[str, int] | None:
    if not story_records:
        return None

    normalized_node = _normalize_rel_path(node_rel_path)
    if not normalized_node:
        target = story_records[0]
        return target["story_rel_path"], int(target["first_page"])

    exact = [item for item in story_records if item["book_rel_path"] == normalized_node]
    if exact:
        target = exact[0]
        return target["story_rel_path"], int(target["first_page"])

    prefix = normalized_node + "/"
    inherited = [item for item in story_records if item["book_rel_path"].startswith(prefix)]
    if inherited:
        target = inherited[0]
        return target["story_rel_path"], int(target["first_page"])

    target = story_records[0]
    return target["story_rel_path"], int(target["first_page"])


def _iter_anchor_records(story_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for meta_file in LIBRARY_ROOT.rglob("meta.json"):
        rel_meta = _normalize_rel_path(meta_file.resolve().relative_to(LIBRARY_ROOT.resolve()).as_posix())
        if _is_in_excluded_area(rel_meta):
            continue

        meta_payload = _read_json_file(meta_file)
        if not meta_payload:
            continue

        node_rel_path = _normalize_rel_path(meta_file.parent.resolve().relative_to(LIBRARY_ROOT.resolve()).as_posix())
        if node_rel_path == ".":
            node_rel_path = ""

        collection = meta_payload.get("collection", {})
        collection_title = ""
        if isinstance(collection, dict):
            collection_title = str(collection.get("title", "")).strip()
        if not collection_title:
            collection_title = node_rel_path or "library"

        anchors = meta_payload.get("anchors", [])
        if not isinstance(anchors, list):
            continue

        anchors_sorted = sorted(
            [item for item in anchors if isinstance(item, dict)],
            key=lambda item: str(item.get("id", "")).strip().lower(),
        )

        for anchor in anchors_sorted:
            anchor_id = str(anchor.get("id", "")).strip()
            if not anchor_id:
                continue

            prompt = str(anchor.get("prompt", "")).strip()
            reference_ids = _coerce_string_list(anchor.get("image_filenames", []))
            state = _slot_state(anchor)

            editor_target = _pick_editor_story_for_anchor(node_rel_path, story_records)
            editor_story_rel_path = editor_target[0] if editor_target else ""
            editor_page = editor_target[1] if editor_target else 1

            rows.append(
                {
                    "item_type": "anchor",
                    "queue_key": f"anchor::{node_rel_path}::{anchor_id}",
                    "book_rel_path": node_rel_path,
                    "story_rel_path": "",
                    "story_id": "",
                    "story_title": "",
                    "page_number": 0,
                    "slot_name": "",
                    "anchor_id": anchor_id,
                    "anchor_node_rel_path": node_rel_path,
                    "prompt": prompt,
                    "status": str(anchor.get("status", "draft")).strip() or "draft",
                    "reference_ids": reference_ids,
                    "reference_assets": _build_reference_assets(node_rel_path, reference_ids),
                    "state": state,
                    "display_title": str(anchor.get("name", "")).strip() or anchor_id,
                    "display_subtitle": f"Ancla · {collection_title}",
                    "editor_story_rel_path": editor_story_rel_path,
                    "editor_page": editor_page,
                }
            )

    rows.sort(key=lambda item: (item["anchor_node_rel_path"], item["anchor_id"]))
    return rows


def _iter_story_slot_records(story_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for story in story_records:
        payload = story["payload"]
        story_rel_path = story["story_rel_path"]
        story_id = story["story_id"]
        story_title = story["title"]
        book_rel_path = story["book_rel_path"]

        cover = payload.get("cover", {})
        if isinstance(cover, dict):
            cover_prompt = str(cover.get("prompt", "")).strip()
            cover_refs = _coerce_string_list(cover.get("reference_ids", []))
            rows.append(
                {
                    "item_type": "cover",
                    "queue_key": f"cover::{story_rel_path}",
                    "book_rel_path": book_rel_path,
                    "story_rel_path": story_rel_path,
                    "story_id": story_id,
                    "story_title": story_title,
                    "page_number": 0,
                    "slot_name": "cover",
                    "anchor_id": "",
                    "anchor_node_rel_path": "",
                    "prompt": cover_prompt,
                    "status": str(cover.get("status", "draft")).strip() or "draft",
                    "reference_ids": cover_refs,
                    "reference_assets": _build_reference_assets(book_rel_path, cover_refs),
                    "state": _slot_state(cover),
                    "display_title": story_title,
                    "display_subtitle": f"Cuento {story_id} · Portada",
                    "editor_story_rel_path": story_rel_path,
                    "editor_page": int(story["first_page"]),
                }
            )

        pages = payload.get("pages", [])
        pages_sorted = sorted(
            [item for item in pages if isinstance(item, dict)],
            key=lambda item: int(item.get("page_number", 0)),
        )

        # main first
        for page in pages_sorted:
            try:
                page_number = int(page.get("page_number", 0))
            except (TypeError, ValueError):
                continue
            if page_number <= 0:
                continue

            images = page.get("images", {})
            if not isinstance(images, dict):
                continue

            main_slot = images.get("main", {})
            if isinstance(main_slot, dict):
                main_prompt = str(main_slot.get("prompt", "")).strip()
                main_refs = _coerce_string_list(main_slot.get("reference_ids", []))
                rows.append(
                    {
                        "item_type": "slot",
                        "queue_key": f"slot::{story_rel_path}::{page_number}::main",
                        "book_rel_path": book_rel_path,
                        "story_rel_path": story_rel_path,
                        "story_id": story_id,
                        "story_title": story_title,
                        "page_number": page_number,
                        "slot_name": "main",
                        "anchor_id": "",
                        "anchor_node_rel_path": "",
                        "prompt": main_prompt,
                        "status": str(main_slot.get("status", "draft")).strip() or "draft",
                        "reference_ids": main_refs,
                        "reference_assets": _build_reference_assets(book_rel_path, main_refs),
                        "state": _slot_state(main_slot),
                        "display_title": story_title,
                        "display_subtitle": f"Cuento {story_id} · Pagina {page_number} · Slot main",
                        "editor_story_rel_path": story_rel_path,
                        "editor_page": page_number,
                    }
                )

        # secondary after all main
        for page in pages_sorted:
            try:
                page_number = int(page.get("page_number", 0))
            except (TypeError, ValueError):
                continue
            if page_number <= 0:
                continue

            images = page.get("images", {})
            if not isinstance(images, dict) or "secondary" not in images:
                continue

            secondary_slot = images.get("secondary", {})
            if not isinstance(secondary_slot, dict):
                continue

            secondary_prompt = str(secondary_slot.get("prompt", "")).strip()
            secondary_refs = _coerce_string_list(secondary_slot.get("reference_ids", []))
            rows.append(
                {
                    "item_type": "slot",
                    "queue_key": f"slot::{story_rel_path}::{page_number}::secondary",
                    "book_rel_path": book_rel_path,
                    "story_rel_path": story_rel_path,
                    "story_id": story_id,
                    "story_title": story_title,
                    "page_number": page_number,
                    "slot_name": "secondary",
                    "anchor_id": "",
                    "anchor_node_rel_path": "",
                    "prompt": secondary_prompt,
                    "status": str(secondary_slot.get("status", "draft")).strip() or "draft",
                    "reference_ids": secondary_refs,
                    "reference_assets": _build_reference_assets(book_rel_path, secondary_refs),
                    "state": _slot_state(secondary_slot),
                    "display_title": story_title,
                    "display_subtitle": f"Cuento {story_id} · Pagina {page_number} · Slot secondary",
                    "editor_story_rel_path": story_rel_path,
                    "editor_page": page_number,
                }
            )

    return rows


def _build_snapshot_uncached() -> dict[str, Any]:
    story_records = _iter_story_records()
    anchor_items = _iter_anchor_records(story_records)
    story_items = _iter_story_slot_records(story_records)
    all_items = anchor_items + story_items

    pending_items: list[dict[str, Any]] = []
    excluded_no_prompt: list[dict[str, Any]] = []
    completed_count = 0

    for item in all_items:
        state = item.get("state", "")
        if state == "completed":
            completed_count += 1
            continue
        if state == "no_prompt":
            excluded_no_prompt.append(
                {
                    "queue_key": item.get("queue_key", ""),
                    "display_title": item.get("display_title", ""),
                    "display_subtitle": item.get("display_subtitle", ""),
                    "item_type": item.get("item_type", ""),
                }
            )
            continue
        if state == "pending":
            pending_items.append(item)

    return {
        "pending_items": pending_items,
        "excluded_no_prompt": excluded_no_prompt,
        "pending_count": len(pending_items),
        "completed_count": completed_count,
        "excluded_no_prompt_count": len(excluded_no_prompt),
        "has_pending": bool(pending_items),
    }


def build_image_flow_snapshot() -> dict[str, Any]:
    if has_request_context():
        cached = getattr(g, "_image_flow_snapshot", None)
        if isinstance(cached, dict):
            return cached
        snapshot = _build_snapshot_uncached()
        g._image_flow_snapshot = snapshot
        return snapshot
    return _build_snapshot_uncached()


def get_image_flow_nav_status() -> dict[str, Any]:
    snapshot = build_image_flow_snapshot()
    return {
        "has_pending": bool(snapshot.get("has_pending")),
        "pending_count": int(snapshot.get("pending_count", 0) or 0),
    }
