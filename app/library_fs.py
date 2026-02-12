from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT, ROOT_DIR

STORY_FILE_PATTERN = re.compile(r"^(\d{2})\.md$", re.IGNORECASE)
LEGACY_PAGE_FILE_PATTERN = re.compile(r"^\d{3}\.md$", re.IGNORECASE)
PAGE_SECTION_PATTERN = re.compile(r"^P(?:a|á)gina\s+(\d{1,2})$", re.IGNORECASE)
H2_PATTERN = re.compile(r"(?im)^##\s+(.+?)\s*$")
H3_PATTERN = re.compile(r"(?im)^###\s+(.+?)\s*$")
H4_PATTERN = re.compile(r"(?im)^####\s+(.+?)\s*$")
H5_PATTERN = re.compile(r"(?im)^#####\s+(.+?)\s*$")
CODE_BLOCK_PATTERN = re.compile(r"(?is)```(?:text|txt|yaml|yml|markdown|md)?\s*\n?(.*?)\n?```")
BULLET_META_PATTERN = re.compile(r"^\s*-\s*([a-z_]+)\s*:\s*(.*)\s*$", re.IGNORECASE)
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
RELEVANT_EXTENSIONS = (".md", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".json")
EXCLUDED_TOP_LEVEL_DIRS = {"_inbox", "_backups"}


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
    story_id: str
    story_file_rel_path: str
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
    is_book_node: bool = False


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


def _is_excluded_rel_path(relative_parts: tuple[str, ...]) -> bool:
    return bool(relative_parts and relative_parts[0] in EXCLUDED_TOP_LEVEL_DIRS)


def _to_project_rel_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def _split_h_sections(raw_text: str, pattern: re.Pattern[str]) -> list[tuple[str, str]]:
    matches = list(pattern.finditer(raw_text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw_text)
        sections.append((match.group(1).strip(), raw_text[start:end].strip("\n")))
    return sections


def _extract_first_code_block(raw_text: str) -> str:
    match = CODE_BLOCK_PATTERN.search(raw_text)
    if not match:
        return ""
    return match.group(1).strip()


def _normalize_role_from_slot(slot_name: str) -> str:
    normalized = slot_name.strip().lower()
    if normalized.startswith("principal"):
        return "principal"
    if normalized.startswith("referencia"):
        return "referencia"
    return "secundaria"


def _slot_slug(slot_name: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", slot_name.lower().strip())
    slug = slug.strip("-")
    return slug or "slot"


def _parse_meta_section(section_text: str) -> dict[str, str]:
    values: dict[str, str] = {
        "estado": "activo",
        "prompt_portada": "",
        "prompt_contraportada": "",
        "notas": "",
    }
    for line in section_text.splitlines():
        match = BULLET_META_PATTERN.match(line)
        if not match:
            continue
        key = match.group(1).strip().lower()
        value = match.group(2).strip()
        values[key] = value
    return values


def _parse_requirements_block(raw_text: str) -> list[RequirementSpec]:
    cleaned = raw_text.strip()
    if not cleaned or cleaned == "[]":
        return []

    requirements: list[RequirementSpec] = []
    current: dict[str, str] = {}

    def _commit_current() -> None:
        kind = current.get("tipo", "").strip()
        ref = current.get("ref", "").strip()
        if kind and ref:
            requirements.append(
                RequirementSpec(
                    kind=kind,
                    ref=ref,
                    order=len(requirements),
                )
            )

    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current:
                _commit_current()
            current = {}
            stripped = stripped[2:].strip()

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        current[key.strip().lower()] = value.strip()

    if current:
        _commit_current()

    return requirements


def story_rel_to_book_and_id(story_rel_path: str) -> tuple[str, str]:
    normalized = story_rel_path.strip().replace("\\", "/").strip("/")
    path_obj = Path(normalized)
    story_id = path_obj.name
    parent = path_obj.parent.as_posix()
    book_rel_path = "" if parent == "." else parent
    return book_rel_path, story_id


def _resolve_slot_image_rel_path(book_rel_path: str, story_id: str, page_number: int, slot_name: str) -> str:
    prefix = f"{story_id}-p{page_number:02d}-{_slot_slug(slot_name)}"
    book_dir = LIBRARY_ROOT / book_rel_path if book_rel_path else LIBRARY_ROOT

    for ext in IMAGE_EXTENSIONS:
        candidate = book_dir / f"{prefix}{ext}"
        if candidate.exists():
            return _to_project_rel_path(candidate)

    return _to_project_rel_path(book_dir / f"{prefix}.png")


def _parse_story_file(story_file: Path, book_rel_path: str) -> StoryData:
    raw_text = story_file.read_text(encoding="utf-8", errors="replace")
    story_id = story_file.stem
    warnings: list[str] = []

    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", raw_text)
    title = title_match.group(1).strip() if title_match else f"Cuento {story_id}"

    meta_raw = ""
    page_sections: list[tuple[int, str]] = []
    for section_name, section_body in _split_h_sections(raw_text, H2_PATTERN):
        if section_name.strip().lower() == "meta":
            meta_raw = section_body
            continue

        page_match = PAGE_SECTION_PATTERN.match(section_name.strip())
        if page_match:
            page_sections.append((int(page_match.group(1)), section_body))

    meta_values = _parse_meta_section(meta_raw)
    story_meta = StoryMeta(
        title=title,
        slug=story_id,
        cover_prompt=meta_values.get("prompt_portada", ""),
        back_cover_prompt=meta_values.get("prompt_contraportada", ""),
        status=meta_values.get("estado", "activo") or "activo",
        notes=meta_values.get("notas", ""),
        raw_frontmatter_json=json.dumps(meta_values, ensure_ascii=False),
    )

    pages: list[StoryPage] = []
    for page_number, page_body in sorted(page_sections, key=lambda item: item[0]):
        if page_number <= 0:
            continue

        page_warnings: list[str] = []
        page_h3 = _split_h_sections(page_body, H3_PATTERN)
        text_body = ""
        prompts_body = ""
        for section_name, section_content in page_h3:
            normalized = section_name.strip().lower()
            if normalized == "texto":
                text_body = section_content.strip()
            elif normalized == "prompts":
                prompts_body = section_content

        if not text_body:
            page_warnings.append("La sección '### Texto' está vacía o ausente.")
        if not prompts_body:
            page_warnings.append("La sección '### Prompts' está vacía o ausente.")

        slots: list[ImageSlotSpec] = []
        for slot_index, (slot_name_raw, slot_body) in enumerate(_split_h_sections(prompts_body, H4_PATTERN)):
            slot_name = slot_name_raw.strip()
            if not slot_name:
                continue

            prompt_text = _extract_first_code_block(slot_body)
            requirement_body = ""
            for h5_name, h5_body in _split_h_sections(slot_body, H5_PATTERN):
                if h5_name.strip().lower() == "requisitos":
                    requirement_body = _extract_first_code_block(h5_body) or h5_body
                    break

            requirements = _parse_requirements_block(requirement_body)
            slots.append(
                ImageSlotSpec(
                    slot_name=slot_name,
                    role=_normalize_role_from_slot(slot_name),
                    prompt_text=prompt_text,
                    requirements=requirements,
                    display_order=slot_index,
                    image_rel_path=_resolve_slot_image_rel_path(
                        book_rel_path=book_rel_path,
                        story_id=story_id,
                        page_number=page_number,
                        slot_name=slot_name,
                    ),
                )
            )

        pages.append(
            StoryPage(
                page_number=page_number,
                file_rel_path=_to_project_rel_path(story_file),
                content=text_body,
                raw_frontmatter_json=json.dumps(
                    {
                        "page_number": page_number,
                        "source": "story_markdown",
                    },
                    ensure_ascii=False,
                ),
                image_slots=slots,
                warnings=page_warnings,
            )
        )

    if not pages:
        warnings.append("No se detectaron secciones de página con formato '## Página NN'.")

    story_rel_path = f"{book_rel_path}/{story_id}" if book_rel_path else story_id
    return StoryData(
        story_rel_path=story_rel_path,
        story_id=story_id,
        story_file_rel_path=_to_project_rel_path(story_file),
        meta_rel_path=_to_project_rel_path(story_file),
        meta=story_meta,
        pages=pages,
        warnings=warnings,
    )


def _is_legacy_story_dir(dir_name: str, file_names: list[str]) -> bool:
    if not re.fullmatch(r"\d{2}", dir_name):
        return False
    if "meta.md" not in file_names:
        return False
    return any(LEGACY_PAGE_FILE_PATTERN.fullmatch(file_name) for file_name in file_names)


def _is_legacy_story_residue(dir_name: str, dir_names: list[str], file_names: list[str]) -> bool:
    if not re.fullmatch(r"\d{2}", dir_name):
        return False
    if any(STORY_FILE_PATTERN.fullmatch(file_name) for file_name in file_names):
        return False
    if not file_names and not dir_names:
        return True
    legacy_subdirs = {"imagenes", "referencias", "textos"}
    return not file_names and set(dir_names).issubset(legacy_subdirs)


def list_relevant_files(root: Path | None = None) -> list[Path]:
    base_root = (root or LIBRARY_ROOT).resolve()
    matches: list[Path] = []

    for entry in base_root.rglob("*"):
        if not entry.is_file():
            continue
        rel_parts = entry.resolve().relative_to(base_root).parts
        if _is_excluded_rel_path(rel_parts):
            continue
        if "_legacy_story_dirs" in rel_parts:
            continue
        if entry.suffix.lower() in RELEVANT_EXTENSIONS:
            matches.append(entry)

    matches.sort(key=lambda item: item.as_posix())
    return matches


def scan_library() -> LibrarySnapshot:
    root = LIBRARY_ROOT.resolve()
    nodes: list[NodeData] = []
    stories: list[StoryData] = []
    warnings: list[str] = []

    for dir_path, dir_names, file_names in os.walk(root):
        dir_names.sort()
        file_names.sort()

        abs_dir = Path(dir_path)
        rel = abs_dir.relative_to(root).as_posix()
        rel = "" if rel == "." else rel

        rel_parts = tuple(Path(rel).parts) if rel else tuple()
        if _is_excluded_rel_path(rel_parts) or "_legacy_story_dirs" in rel_parts:
            dir_names[:] = []
            continue

        if _is_legacy_story_dir(abs_dir.name, file_names):
            dir_names[:] = []
            continue
        if _is_legacy_story_residue(abs_dir.name, dir_names, file_names):
            dir_names[:] = []
            continue

        parent_rel = Path(rel).parent.as_posix() if rel else None
        if parent_rel == ".":
            parent_rel = ""

        story_files = sorted(
            file_name for file_name in file_names if STORY_FILE_PATTERN.fullmatch(file_name)
        )
        is_book_node = bool(story_files)

        nodes.append(
            NodeData(
                path_rel=rel,
                parent_path_rel=parent_rel,
                name=abs_dir.name if rel else "biblioteca",
                is_story_leaf=False,
                is_book_node=is_book_node,
            )
        )

        if not is_book_node:
            continue

        for story_file_name in story_files:
            story_file = abs_dir / story_file_name
            story = _parse_story_file(story_file=story_file, book_rel_path=rel)
            stories.append(story)

            nodes.append(
                NodeData(
                    path_rel=story.story_rel_path,
                    parent_path_rel=rel,
                    name=story.story_id,
                    is_story_leaf=True,
                    is_book_node=False,
                )
            )

            warnings.extend(f"[{story.story_rel_path}] {item}" for item in story.warnings)
            for page in story.pages:
                warnings.extend(
                    f"[{story.story_rel_path}/p{page.page_number:02d}] {item}"
                    for item in page.warnings
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

    nodes.sort(key=lambda item: (item.path_rel.count("/"), item.path_rel, item.is_story_leaf))
    stories.sort(key=lambda item: item.story_rel_path)
    assets.sort(key=lambda item: item.rel_path)
    return LibrarySnapshot(nodes=nodes, stories=stories, assets=assets, warnings=warnings)


def resolve_requirement_paths(story_rel_path: str, ref_value: str) -> list[str]:
    ref = ref_value.strip().replace("\\", "/")
    if not ref:
        return []

    book_rel_path, _ = story_rel_to_book_and_id(story_rel_path)
    book_dir = (LIBRARY_ROOT / book_rel_path).resolve() if book_rel_path else LIBRARY_ROOT.resolve()

    candidates: list[Path] = []
    ref_path = Path(ref)
    if ref_path.is_absolute():
        candidates.append(ref_path)
    else:
        candidates.append((book_dir / ref).resolve())
        candidates.append((LIBRARY_ROOT / ref).resolve())
        candidates.append((ROOT_DIR / ref).resolve())
        candidates.append((ROOT_DIR / "library" / ref).resolve())

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
