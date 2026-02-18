from __future__ import annotations

from typing import Any

from flask import url_for

from ..catalog_provider import get_story_summary
from ..story_store import StoryStoreError, list_story_pages


def normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def safe_next_url(raw_value: str | None, fallback_url: str) -> str:
    value = (raw_value or "").strip()
    if not value.startswith("/") or value.startswith("//"):
        return fallback_url
    return value


def parse_positive_int(raw_value: str | None, default: int) -> int:
    try:
        value = int(str(raw_value))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def is_editor_mode(raw_value: str | None) -> bool:
    value = (raw_value or "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def build_breadcrumbs(path_rel: str) -> list[dict[str, str]]:
    normalized = normalize_rel_path(path_rel)
    if not normalized:
        return [{"name": "biblioteca", "path": ""}]

    parts = [part for part in normalized.split("/") if part]
    crumbs = [{"name": "biblioteca", "path": ""}]
    current: list[str] = []
    for part in parts:
        current.append(part)
        crumbs.append({"name": part, "path": "/".join(current)})
    return crumbs


def build_story_url(story_rel_path: str, *, page_number: int | None = None, editor_mode: bool = False) -> str:
    normalized = normalize_rel_path(story_rel_path)
    args: dict[str, Any] = {"path_rel": normalized}
    if page_number is not None and int(page_number) > 0:
        args["p"] = int(page_number)
    if editor_mode:
        args["editor"] = 1
    return url_for("web.node_or_story", **args)


def first_story_page_number(story_rel_path: str) -> int:
    try:
        pages = list_story_pages(story_rel_path)
    except (FileNotFoundError, StoryStoreError):
        return 1
    if not pages:
        return 1
    return int(pages[0]["page_number"])


def decorate_children_for_cards(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for child in children:
        item = dict(child)
        path_rel = normalize_rel_path(str(item.get("path_rel", "")))

        if item.get("is_story_leaf"):
            summary = item.get("story_summary") or get_story_summary(path_rel) or {}
            item["href"] = build_story_url(path_rel)
            item["card_title"] = str(summary.get("title", "")).strip() or str(item.get("name", "")).strip()
            story_id = str(summary.get("story_id", "")).strip()
            item["card_subtitle"] = f"Cuento {story_id}" if story_id else "Cuento"
            item["story_status"] = str(summary.get("status", "draft"))
            item["story_pages"] = int(summary.get("pages", 0) or 0)
            item["story_slots"] = int(summary.get("slots", 0) or 0)
            item["story_alternatives"] = int(summary.get("alternatives", 0) or 0)

            thumb_rel_path = str(summary.get("thumb_rel_path", "")).strip().replace("\\", "/")
            item["thumb_url"] = (
                url_for("web.media_file", rel_path=thumb_rel_path)
                if thumb_rel_path and bool(summary.get("thumb_exists"))
                else ""
            )
            item["thumb_source"] = str(summary.get("thumb_source", "placeholder")).strip() or "placeholder"
            item["thumb_rel_path"] = thumb_rel_path
            item["card_kind"] = "story"
        else:
            item["href"] = url_for("web.node_or_story", path_rel=path_rel) if path_rel else url_for("web.dashboard")
            item["card_title"] = str(item.get("name", "")).strip() or "(sin nombre)"
            if item.get("is_book_node"):
                item["card_subtitle"] = "Libro"
                item["card_kind"] = "book"
            else:
                item["card_subtitle"] = "Nodo"
                item["card_kind"] = "node"

        items.append(item)

    return items
