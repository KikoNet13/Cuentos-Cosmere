from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT, ROOT_DIR

PAGE_FILE_PATTERN = re.compile(r"^(\d{3})\.md$")
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
RELEVANT_EXTENSIONS = (".md", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".json")


@dataclass
class RequirementSpec:
    kind: str
    ref: str
    order: int = 0


@dataclass
class ImageSlotSpec:
    slot_name: str
    role: str
    prompt_text: str
    requirements: list[RequirementSpec] = field(default_factory=list)
    display_order: int = 0
    image_rel_path: str = ""


@dataclass
class StoryPage:
    page_number: int
    file_rel_path: str
    content: str
    raw_frontmatter_json: str
    image_slots: list[ImageSlotSpec]
    warnings: list[str] = field(default_factory=list)


@dataclass
class StoryMeta:
    title: str
    slug: str
    cover_prompt: str
    back_cover_prompt: str
    status: str
    notes: str
    raw_frontmatter_json: str


@dataclass
class StoryData:
    story_rel_path: str
    meta_rel_path: str
    meta: StoryMeta
    pages: list[StoryPage]
    warnings: list[str] = field(default_factory=list)


@dataclass
class NodeData:
    path_rel: str
    parent_path_rel: str | None
    name: str
    is_story_leaf: bool


@dataclass
class AssetInfo:
    rel_path: str
    kind: str
    size: int
    mtime_ns: int
    is_present: bool


@dataclass
class LibrarySnapshot:
    nodes: list[NodeData]
    stories: list[StoryData]
    assets: list[AssetInfo]
    warnings: list[str]


def list_relevant_files(root: Path | None = None) -> list[Path]:
    base_root = (root or LIBRARY_ROOT).resolve()
    matches: list[Path] = []
    for entry in base_root.rglob("*"):
        if entry.is_file() and entry.suffix.lower() in RELEVANT_EXTENSIONS:
            matches.append(entry)
    matches.sort(key=lambda item: item.as_posix())
    return matches


def _to_project_rel_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def _slot_slug(slot_name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", slot_name.lower().strip())
    slug = slug.strip("-")
    return slug or "slot"


def _normalize_role(raw_value: str) -> str:
    value = raw_value.strip().lower()
    if value in {"principal", "secundaria", "referencia"}:
        return value
    return "secundaria"


def _parse_key_value(line: str) -> tuple[str, str] | None:
    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    key = key.strip()
    if not key:
        return None
    return key, value.strip()


def _parse_scalar(raw_value: str) -> str:
    value = raw_value.strip()
    if value == "":
        return ""
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1].replace('\\"', '"')
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1].replace("\\'", "'")
    return value


def _split_frontmatter(raw_text: str) -> tuple[list[str], str, list[str]]:
    warnings: list[str] = []
    lines = raw_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], raw_text, warnings

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        warnings.append("Frontmatter sin cierre '---'.")
        return [], raw_text, warnings

    frontmatter_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return frontmatter_lines, body, warnings


def _parse_meta_frontmatter(lines: list[str]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    raw_meta: dict[str, Any] = {}

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        parsed = _parse_key_value(clean_line)
        if not parsed:
            warnings.append(f"Línea inválida en frontmatter de meta: {line}")
            continue
        key, value = parsed
        raw_meta[key] = _parse_scalar(value)

    mapped = {
        "title": str(raw_meta.get("titulo", "")),
        "slug": str(raw_meta.get("slug", "")),
        "cover_prompt": str(raw_meta.get("prompt_portada", "")),
        "back_cover_prompt": str(raw_meta.get("prompt_contraportada", "")),
        "status": str(raw_meta.get("estado", "activo")),
    }
    return mapped, warnings


def _parse_page_frontmatter(lines: list[str]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    mapped: dict[str, Any] = {
        "page_number": None,
        "image_slots": [],
    }

    index = 0
    total = len(lines)
    while index < total:
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped:
            index += 1
            continue

        parsed = _parse_key_value(stripped)
        if not parsed:
            warnings.append(f"Línea inválida en frontmatter de página: {raw_line}")
            index += 1
            continue

        key, value = parsed
        if key != "imagenes":
            if key == "pagina":
                mapped["page_number"] = _parse_scalar(value)
            index += 1
            continue

        if value and value != "[]":
            warnings.append("El campo 'imagenes' debe usar lista en bloque o [].")
        if value == "[]":
            index += 1
            continue

        index += 1
        slot_order = 0
        while index < total and lines[index].startswith("  - "):
            slot_item: dict[str, Any] = {
                "slot_name": "",
                "role": "secundaria",
                "prompt_text": "",
                "requirements": [],
                "display_order": slot_order,
            }
            first_inline = lines[index][4:].strip()
            if first_inline:
                kv = _parse_key_value(first_inline)
                if kv:
                    k, v = kv
                    scalar = _parse_scalar(v)
                    if k == "slot":
                        slot_item["slot_name"] = scalar
                    elif k == "rol":
                        slot_item["role"] = scalar
                    elif k == "prompt":
                        slot_item["prompt_text"] = scalar
            index += 1

            while index < total and lines[index].startswith("    "):
                field_line = lines[index][4:].strip()
                if not field_line:
                    index += 1
                    continue

                if field_line.startswith("requisitos:"):
                    requirement_value = field_line.split(":", 1)[1].strip()
                    if requirement_value == "[]":
                        index += 1
                        continue
                    if requirement_value not in {"", "[]"}:
                        warnings.append(
                            f"Formato de requisitos no soportado: {field_line}"
                        )
                        index += 1
                        continue

                    index += 1
                    requirement_order = 0
                    while index < total and lines[index].startswith("      - "):
                        requirement_item: dict[str, Any] = {
                            "kind": "",
                            "ref": "",
                            "order": requirement_order,
                        }
                        first_requirement = lines[index][8:].strip()
                        if first_requirement:
                            req_kv = _parse_key_value(first_requirement)
                            if req_kv:
                                req_key, req_value = req_kv
                                scalar = _parse_scalar(req_value)
                                if req_key == "tipo":
                                    requirement_item["kind"] = scalar
                                elif req_key == "ref":
                                    requirement_item["ref"] = scalar
                        index += 1

                        while index < total and lines[index].startswith("        "):
                            sub_line = lines[index][8:].strip()
                            sub_kv = _parse_key_value(sub_line) if sub_line else None
                            if sub_kv:
                                sub_key, sub_value = sub_kv
                                scalar = _parse_scalar(sub_value)
                                if sub_key == "tipo":
                                    requirement_item["kind"] = scalar
                                elif sub_key == "ref":
                                    requirement_item["ref"] = scalar
                            index += 1

                        if requirement_item["kind"] and requirement_item["ref"]:
                            slot_item["requirements"].append(requirement_item)
                            requirement_order += 1
                    continue

                field_kv = _parse_key_value(field_line)
                if field_kv:
                    field_key, field_value = field_kv
                    scalar = _parse_scalar(field_value)
                    if field_key == "slot":
                        slot_item["slot_name"] = scalar
                    elif field_key == "rol":
                        slot_item["role"] = scalar
                    elif field_key == "prompt":
                        slot_item["prompt_text"] = scalar
                else:
                    warnings.append(f"Campo de imagen inválido: {field_line}")
                index += 1

            slot_name = str(slot_item.get("slot_name", "")).strip()
            if not slot_name:
                warnings.append("Imagen sin slot en frontmatter de página.")
                continue

            slot_item["slot_name"] = slot_name
            slot_item["role"] = _normalize_role(str(slot_item.get("role", "")))
            mapped["image_slots"].append(slot_item)
            slot_order += 1

    return mapped, warnings


def _resolve_slot_image_rel_path(story_rel_path: str, page_number: int, slot_name: str) -> str:
    story_dir = LIBRARY_ROOT / story_rel_path
    images_dir = story_dir / "assets" / "imagenes"
    base_name = f"pagina-{page_number:03d}-{_slot_slug(slot_name)}"

    for ext in IMAGE_EXTENSIONS:
        candidate = images_dir / f"{base_name}{ext}"
        if candidate.exists():
            return _to_project_rel_path(candidate)

    return _to_project_rel_path(images_dir / f"{base_name}.png")


def load_story(story_rel_path: str) -> StoryData:
    story_dir = LIBRARY_ROOT / story_rel_path
    story_warnings: list[str] = []

    raw_meta = (story_dir / "meta.md").read_text(encoding="utf-8", errors="replace")
    meta_lines, meta_body, split_warnings = _split_frontmatter(raw_meta)
    story_warnings.extend(split_warnings)

    meta_data, meta_warnings = _parse_meta_frontmatter(meta_lines)
    story_warnings.extend(meta_warnings)

    story_meta = StoryMeta(
        title=meta_data["title"] or story_dir.name,
        slug=meta_data["slug"] or story_dir.name,
        cover_prompt=meta_data["cover_prompt"],
        back_cover_prompt=meta_data["back_cover_prompt"],
        status=meta_data["status"] or "activo",
        notes=meta_body.strip(),
        raw_frontmatter_json=json.dumps(meta_data, ensure_ascii=False),
    )

    pages: list[StoryPage] = []
    for page_file in sorted(story_dir.iterdir(), key=lambda item: item.name):
        if not page_file.is_file():
            continue
        match = PAGE_FILE_PATTERN.fullmatch(page_file.name)
        if not match:
            continue

        file_page_number = int(match.group(1))
        raw_page = page_file.read_text(encoding="utf-8", errors="replace")
        page_lines, page_body, page_split_warnings = _split_frontmatter(raw_page)
        page_frontmatter, page_parse_warnings = _parse_page_frontmatter(page_lines)

        page_warnings = list(page_split_warnings) + list(page_parse_warnings)
        declared_raw = str(page_frontmatter.get("page_number", "")).strip()
        if declared_raw:
            try:
                declared_page_number = int(declared_raw)
                if declared_page_number > 0 and declared_page_number != file_page_number:
                    page_warnings.append(
                        (
                            "La página declarada "
                            f"{declared_page_number} no coincide con el archivo "
                            f"{file_page_number:03d}; se usa {file_page_number:03d}."
                        )
                    )
            except ValueError:
                page_warnings.append(
                    f"Valor de página inválido en frontmatter: '{declared_raw}'."
                )

        slots: list[ImageSlotSpec] = []
        for slot_item in page_frontmatter.get("image_slots", []):
            slot_name = str(slot_item.get("slot_name", "")).strip()
            if not slot_name:
                continue

            requirements: list[RequirementSpec] = []
            for requirement in slot_item.get("requirements", []):
                kind = str(requirement.get("kind", "")).strip()
                ref = str(requirement.get("ref", "")).strip()
                if not kind or not ref:
                    continue
                requirements.append(
                    RequirementSpec(
                        kind=kind,
                        ref=ref,
                        order=int(requirement.get("order", 0)),
                    )
                )

            slots.append(
                ImageSlotSpec(
                    slot_name=slot_name,
                    role=_normalize_role(str(slot_item.get("role", ""))),
                    prompt_text=str(slot_item.get("prompt_text", "")),
                    requirements=requirements,
                    display_order=int(slot_item.get("display_order", 0)),
                    image_rel_path=_resolve_slot_image_rel_path(
                        story_rel_path,
                        file_page_number,
                        slot_name,
                    ),
                )
            )

        pages.append(
            StoryPage(
                page_number=file_page_number,
                file_rel_path=_to_project_rel_path(page_file),
                content=page_body.strip(),
                raw_frontmatter_json=json.dumps(page_frontmatter, ensure_ascii=False),
                image_slots=slots,
                warnings=page_warnings,
            )
        )

    pages.sort(key=lambda item: item.page_number)
    return StoryData(
        story_rel_path=story_rel_path,
        meta_rel_path=_to_project_rel_path(story_dir / "meta.md"),
        meta=story_meta,
        pages=pages,
        warnings=story_warnings,
    )


def scan_library() -> LibrarySnapshot:
    root = LIBRARY_ROOT.resolve()
    nodes: list[NodeData] = []
    stories: list[StoryData] = []
    warnings: list[str] = []

    for dir_path, dir_names, file_names in os.walk(root):
        dir_names.sort()
        file_names.sort()

        absolute_dir = Path(dir_path)
        rel = absolute_dir.relative_to(root).as_posix()
        rel = "" if rel == "." else rel

        parent_rel = Path(rel).parent.as_posix() if rel else None
        if parent_rel == ".":
            parent_rel = ""

        is_story_leaf = (
            "meta.md" in file_names
            and any(PAGE_FILE_PATTERN.fullmatch(file_name) for file_name in file_names)
        )

        nodes.append(
            NodeData(
                path_rel=rel,
                parent_path_rel=parent_rel,
                name=absolute_dir.name if rel else "biblioteca",
                is_story_leaf=is_story_leaf,
            )
        )

        if is_story_leaf:
            story = load_story(rel)
            stories.append(story)
            warnings.extend(f"[{rel}] {item}" for item in story.warnings)
            for page in story.pages:
                warnings.extend(
                    f"[{rel}/{page.page_number:03d}] {item}" for item in page.warnings
                )

    assets: list[AssetInfo] = []
    for file_path in list_relevant_files(root):
        stat = file_path.stat()
        ext = file_path.suffix.lower()
        kind = "other"
        if ext == ".md":
            kind = "md"
        elif ext == ".pdf":
            kind = "pdf"
        elif ext in IMAGE_EXTENSIONS:
            kind = "image"
        elif ext == ".json":
            kind = "json"

        assets.append(
            AssetInfo(
                rel_path=_to_project_rel_path(file_path),
                kind=kind,
                size=int(stat.st_size),
                mtime_ns=int(stat.st_mtime_ns),
                is_present=True,
            )
        )

    nodes.sort(key=lambda item: (item.path_rel.count("/"), item.path_rel))
    stories.sort(key=lambda item: item.story_rel_path)
    assets.sort(key=lambda item: item.rel_path)
    return LibrarySnapshot(nodes=nodes, stories=stories, assets=assets, warnings=warnings)


def resolve_requirement_paths(story_rel_path: str, ref_value: str) -> list[str]:
    ref = ref_value.strip().replace("\\", "/")
    if not ref:
        return []

    story_dir = (LIBRARY_ROOT / story_rel_path).resolve()
    candidates: list[Path] = []

    ref_path = Path(ref)
    if ref_path.is_absolute():
        candidates.append(ref_path)
    else:
        candidates.append((story_dir / ref).resolve())
        candidates.append((LIBRARY_ROOT / ref).resolve())
        candidates.append((ROOT_DIR / ref).resolve())
        candidates.append((ROOT_DIR / "biblioteca" / ref).resolve())

    project_root = ROOT_DIR.resolve()
    resolved: list[str] = []
    for candidate in candidates:
        if not candidate.exists():
            continue

        if candidate.is_file():
            if candidate.suffix.lower() in IMAGE_EXTENSIONS and project_root in candidate.parents:
                rel_path = candidate.relative_to(project_root).as_posix()
                if rel_path not in resolved:
                    resolved.append(rel_path)
            continue

        if candidate.is_dir():
            for item in sorted(candidate.iterdir()):
                if not item.is_file():
                    continue
                if item.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                if project_root not in item.parents:
                    continue
                rel_path = item.relative_to(project_root).as_posix()
                if rel_path not in resolved:
                    resolved.append(rel_path)

    return resolved
