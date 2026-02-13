from __future__ import annotations

import re
from pathlib import Path

from .config import LIBRARY_ROOT, ROOT_DIR

STORY_JSON_PATTERN = re.compile(r"^(\d{2})\.json$", re.IGNORECASE)
EXCLUDED_TOP_LEVEL_DIRS = {"_inbox", "_backups"}
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def story_rel_to_book_and_id(story_rel_path: str) -> tuple[str, str]:
    normalized = _normalize_rel_path(story_rel_path)
    path_obj = Path(normalized)
    story_id = path_obj.name
    parent = path_obj.parent.as_posix()
    book_rel_path = "" if parent == "." else parent
    return book_rel_path, story_id


def list_story_json_files(root: Path | None = None) -> list[Path]:
    base_root = (root or LIBRARY_ROOT).resolve()
    matches: list[Path] = []

    if not base_root.exists():
        return matches

    for entry in base_root.rglob("*.json"):
        if not entry.is_file():
            continue
        rel_parts = entry.resolve().relative_to(base_root).parts
        if rel_parts and rel_parts[0] in EXCLUDED_TOP_LEVEL_DIRS:
            continue
        if not STORY_JSON_PATTERN.fullmatch(entry.name):
            continue
        matches.append(entry)

    matches.sort(key=lambda item: item.as_posix())
    return matches


def resolve_story_asset_candidates(story_rel_path: str, ref_value: str) -> list[str]:
    ref = ref_value.strip().replace("\\", "/")
    if not ref:
        return []

    candidates: list[str] = []

    abs_ref = (ROOT_DIR / ref).resolve()
    root_abs = ROOT_DIR.resolve()
    if abs_ref.exists() and (root_abs in abs_ref.parents or abs_ref == root_abs):
        candidates.append(abs_ref.relative_to(root_abs).as_posix())

    book_rel_path, _ = story_rel_to_book_and_id(story_rel_path)
    if book_rel_path:
        book_candidate = (LIBRARY_ROOT / book_rel_path / ref).resolve()
        if book_candidate.exists() and (root_abs in book_candidate.parents or book_candidate == root_abs):
            rel = book_candidate.relative_to(root_abs).as_posix()
            if rel not in candidates:
                candidates.append(rel)

    return candidates


def slot_slug(slot_name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", slot_name.lower().strip())
    slug = slug.strip("-")
    return slug or "slot"
