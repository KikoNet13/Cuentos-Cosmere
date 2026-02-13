from __future__ import annotations

from pathlib import Path
from typing import Any

from .story_store import StoryStoreError, json_path_to_story_rel, list_story_json_files, load_story


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _node_name(path_rel: str) -> str:
    if not path_rel:
        return "biblioteca"
    return path_rel.split("/")[-1]


def _parent_path(path_rel: str) -> str | None:
    if not path_rel:
        return None
    path = Path(path_rel)
    parent = path.parent.as_posix()
    if parent == ".":
        return ""
    return parent


def _new_node(path_rel: str) -> dict[str, Any]:
    return {
        "path_rel": path_rel,
        "parent_path_rel": _parent_path(path_rel),
        "name": _node_name(path_rel),
        "is_story_leaf": False,
        "is_book_node": False,
    }


def _ensure_node(nodes: dict[str, dict[str, Any]], path_rel: str) -> dict[str, Any]:
    normalized = _normalize_rel_path(path_rel)
    if normalized not in nodes:
        nodes[normalized] = _new_node(normalized)
    return nodes[normalized]


def _story_counts(story_payload: dict[str, Any]) -> tuple[int, int, int]:
    pages_count = len(story_payload.get("pages", []))
    slots_count = 0
    alternatives_count = 0

    for page in story_payload.get("pages", []):
        images = page.get("images", {})
        for slot_name in ("main", "secondary"):
            slot = images.get(slot_name)
            if not isinstance(slot, dict):
                continue
            slots_count += 1
            alternatives_count += len(slot.get("alternatives", []))

    return pages_count, slots_count, alternatives_count


def _build_catalog() -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    stories: dict[str, dict[str, Any]] = {}

    _ensure_node(nodes, "")

    pages_total = 0
    slots_total = 0
    alternatives_total = 0

    for story_file in list_story_json_files():
        try:
            story_rel_path = json_path_to_story_rel(story_file)
            story_payload = load_story(story_rel_path)
        except (FileNotFoundError, StoryStoreError, ValueError):
            continue

        story_id = str(story_payload.get("story_id", "")).strip() or Path(story_rel_path).name
        title = str(story_payload.get("title", "")).strip() or f"Cuento {story_id}"
        status = str(story_payload.get("status", "draft")).strip() or "draft"
        book_rel_path = _normalize_rel_path(str(story_payload.get("book_rel_path", "")))

        pages_count, slots_count, alternatives_count = _story_counts(story_payload)
        pages_total += pages_count
        slots_total += slots_count
        alternatives_total += alternatives_count

        stories[story_rel_path] = {
            "story_rel_path": story_rel_path,
            "story_id": story_id,
            "title": title,
            "status": status,
            "book_rel_path": book_rel_path,
            "pages": pages_count,
            "slots": slots_count,
            "alternatives": alternatives_count,
        }

        if book_rel_path:
            current = ""
            for part in [item for item in book_rel_path.split("/") if item]:
                current = f"{current}/{part}".strip("/")
                _ensure_node(nodes, current)

        book_node = _ensure_node(nodes, book_rel_path)
        book_node["is_book_node"] = True

        story_node = _ensure_node(nodes, story_rel_path)
        story_node["is_story_leaf"] = True
        story_node["name"] = story_id

    counts = {
        "nodes": len(nodes),
        "stories": len(stories),
        "pages": pages_total,
        "slots": slots_total,
        "alternatives": alternatives_total,
    }

    return {
        "nodes": nodes,
        "stories": stories,
        "counts": counts,
    }


def catalog_counts() -> dict[str, int]:
    return _build_catalog()["counts"]


def get_node(path_rel: str) -> dict[str, Any] | None:
    catalog = _build_catalog()
    normalized = _normalize_rel_path(path_rel)
    return catalog["nodes"].get(normalized)


def list_children(parent_path_rel: str) -> list[dict[str, Any]]:
    catalog = _build_catalog()
    parent = _normalize_rel_path(parent_path_rel)

    rows = [
        node
        for node in catalog["nodes"].values()
        if (node.get("parent_path_rel") or "") == parent and node.get("path_rel") != parent
    ]
    rows.sort(key=lambda item: (0 if not item["is_story_leaf"] else 1, item["name"].lower()))
    return rows


def get_story_summary(story_rel_path: str) -> dict[str, Any] | None:
    catalog = _build_catalog()
    normalized = _normalize_rel_path(story_rel_path)
    return catalog["stories"].get(normalized)
