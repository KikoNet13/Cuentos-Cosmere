from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT
from .text_pages import parse_markdown_pages
from .utils import read_text_with_fallback

LEGACY_TEXTS_DIR = "textos"
LEGACY_SOURCE_MD = "origen_md.md"
LEGACY_PDF_NAMES = ("referencia.pdf", "referencia_pdf.pdf")
LEGACY_PAGE_FILE_RE = re.compile(r"^(\d{3})\.md$", re.IGNORECASE)
STORY_DIR_RE = re.compile(r"^\d{2}$")
LEGACY_IMAGE_NAME_RE = re.compile(
    r"(?i)^(?:pagina[-_])?(\d{1,3})[-_](principal|secundaria(?:[-_]\d{1,2})?|referencia(?:[-_]\d{1,2})?)\.(png|jpg|jpeg|webp)$"
)


@dataclass
class LegacySlot:
    slot_name: str
    role: str
    prompt_text: str
    requirements: list[dict[str, str]] = field(default_factory=list)


@dataclass
class LegacyPage:
    page_number: int
    content: str
    slots: list[LegacySlot]


@dataclass
class StoryMetaData:
    title: str
    status: str
    cover_prompt: str
    back_cover_prompt: str
    notes: str


def _slot_slug(raw_value: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", raw_value.strip().lower())
    slug = slug.strip("-")
    return slug or "principal"


def _normalize_notes(notes: str) -> str:
    value = " ".join(notes.split())
    return value


def _split_frontmatter(raw_text: str) -> tuple[str, str]:
    lines = raw_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", raw_text

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return "", raw_text

    frontmatter = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return frontmatter, body


def _parse_scalar(raw_value: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if len(value) >= 2 and value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _parse_legacy_meta(story_dir: Path, story_id: str) -> StoryMetaData:
    meta_path = story_dir / "meta.md"
    if not meta_path.exists():
        return StoryMetaData(
            title=f"Cuento {story_id}",
            status="activo",
            cover_prompt="",
            back_cover_prompt="",
            notes="",
        )

    raw_meta = read_text_with_fallback(meta_path)
    frontmatter, body = _split_frontmatter(raw_meta)

    values: dict[str, str] = {}
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip().lower()] = _parse_scalar(value)

    return StoryMetaData(
        title=values.get("titulo", f"Cuento {story_id}"),
        status=values.get("estado", "activo") or "activo",
        cover_prompt=values.get("prompt_portada", ""),
        back_cover_prompt=values.get("prompt_contraportada", ""),
        notes=body.strip(),
    )


def _parse_legacy_requirements(raw_text: str) -> list[dict[str, str]]:
    text = raw_text.strip()
    if not text or text == "[]":
        return []

    requirements: list[dict[str, str]] = []
    current: dict[str, str] = {}

    def _commit() -> None:
        tipo = current.get("tipo", "").strip()
        ref = current.get("ref", "").strip()
        if tipo and ref:
            requirements.append({"tipo": tipo, "ref": ref})

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("- "):
            if current:
                _commit()
            current = {}
            stripped = stripped[2:].strip()

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        current[key.strip().lower()] = value.strip()

    if current:
        _commit()

    return requirements


def _parse_legacy_page(page_file: Path) -> LegacyPage:
    raw_page = read_text_with_fallback(page_file)
    frontmatter, body = _split_frontmatter(raw_page)

    page_number = int(page_file.stem)
    slots: list[LegacySlot] = []

    lines = frontmatter.splitlines()
    index = 0
    total = len(lines)
    while index < total:
        line = lines[index].strip()
        if line.startswith("pagina:"):
            value = line.split(":", 1)[1].strip()
            if value.isdigit():
                page_number = int(value)
            index += 1
            continue

        if line.startswith("- slot:"):
            slot_name = _parse_scalar(line.split(":", 1)[1])
            role = "secundaria"
            prompt_text = ""
            requirements: list[dict[str, str]] = []
            index += 1

            while index < total and lines[index].startswith("    "):
                field_line = lines[index].strip()
                if field_line.startswith("rol:"):
                    role = _parse_scalar(field_line.split(":", 1)[1])
                elif field_line.startswith("prompt:"):
                    prompt_text = _parse_scalar(field_line.split(":", 1)[1])
                elif field_line.startswith("requisitos:"):
                    value = field_line.split(":", 1)[1].strip()
                    if value == "[]":
                        requirements = []
                        index += 1
                        continue

                    req_lines: list[str] = []
                    index += 1
                    while index < total and lines[index].startswith("      "):
                        req_lines.append(lines[index].strip())
                        index += 1
                    requirements = _parse_legacy_requirements("\n".join(req_lines))
                    continue
                index += 1

            slots.append(
                LegacySlot(
                    slot_name=slot_name,
                    role=role,
                    prompt_text=prompt_text,
                    requirements=requirements,
                )
            )
            continue

        index += 1

    return LegacyPage(
        page_number=page_number,
        content=body.strip(),
        slots=slots,
    )


def _render_requirements_yaml(requirements: list[dict[str, str]]) -> str:
    if not requirements:
        return "[]"
    lines: list[str] = []
    for req in requirements:
        lines.append(f"- tipo: {req['tipo']}")
        lines.append(f"  ref: {req['ref']}")
    return "\n".join(lines)


def _render_story_markdown(meta: StoryMetaData, pages: list[LegacyPage]) -> str:
    lines: list[str] = [
        f"# {meta.title}",
        "",
        "## Meta",
        f"- estado: {meta.status}",
        f"- prompt_portada: {meta.cover_prompt}",
        f"- prompt_contraportada: {meta.back_cover_prompt}",
        f"- notas: {_normalize_notes(meta.notes)}",
        "",
    ]

    for page in sorted(pages, key=lambda item: item.page_number):
        page_slots = page.slots or [
            LegacySlot(
                slot_name="principal",
                role="principal",
                prompt_text="",
                requirements=[],
            )
        ]

        lines.extend(
            [
                f"## Página {page.page_number:02d}",
                "",
                "### Texto",
                page.content,
                "",
                "### Prompts",
                "",
            ]
        )

        for slot in page_slots:
            lines.extend(
                [
                    f"#### {slot.slot_name}",
                    "```text",
                    slot.prompt_text,
                    "```",
                    "",
                    "##### Requisitos",
                    "```yaml",
                    _render_requirements_yaml(slot.requirements),
                    "```",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"


def _story_pdf_source(story_dir: Path) -> Path | None:
    for base in ((story_dir / "referencias"), (story_dir / LEGACY_TEXTS_DIR)):
        for name in LEGACY_PDF_NAMES:
            candidate = base / name
            if candidate.exists():
                return candidate
    return None


def _target_image_name(story_id: str, source_name: str, fallback_index: int) -> tuple[str, str | None]:
    match = LEGACY_IMAGE_NAME_RE.fullmatch(source_name)
    if not match:
        extension = Path(source_name).suffix.lower() or ".png"
        return f"{story_id}-asset-{fallback_index:02d}{extension}", (
            f"Nombre de imagen legacy no reconocible: {source_name}. "
            "Se conserva como asset genérico."
        )

    page_number = max(1, int(match.group(1)))
    slot_slug = _slot_slug(match.group(2).replace("_", "-"))
    extension = f".{match.group(3).lower()}"
    return f"{story_id}-p{page_number:02d}-{slot_slug}{extension}", None


def _collect_legacy_pages(story_dir: Path, warnings: list[str]) -> list[LegacyPage]:
    page_files = sorted(
        file for file in story_dir.iterdir() if file.is_file() and LEGACY_PAGE_FILE_RE.fullmatch(file.name)
    )
    if page_files:
        return [_parse_legacy_page(page_file) for page_file in page_files]

    source_md = story_dir / LEGACY_TEXTS_DIR / LEGACY_SOURCE_MD
    if source_md.exists():
        markdown = read_text_with_fallback(source_md)
        pages_map, parse_warnings = parse_markdown_pages(markdown)
        warnings.extend(f"[{story_dir}] {item}" for item in parse_warnings)
        return [
            LegacyPage(
                page_number=page_number,
                content=content,
                slots=[
                    LegacySlot(
                        slot_name="principal",
                        role="principal",
                        prompt_text="",
                        requirements=[],
                    )
                ],
            )
            for page_number, content in sorted(pages_map.items())
        ]

    warnings.append(f"[{story_dir}] No se detectaron páginas legacy para migrar.")
    return []


def _legacy_book_dirs(root: Path) -> list[Path]:
    book_dirs: set[Path] = set()

    for source_md in root.rglob(LEGACY_SOURCE_MD):
        if "_legacy_story_dirs" in source_md.parts:
            continue
        story_dir = source_md.parent.parent
        if STORY_DIR_RE.fullmatch(story_dir.name):
            book_dirs.add(story_dir.parent)

    for meta_file in root.rglob("meta.md"):
        if "_legacy_story_dirs" in meta_file.parts:
            continue
        story_dir = meta_file.parent
        if not STORY_DIR_RE.fullmatch(story_dir.name):
            continue
        if any(LEGACY_PAGE_FILE_RE.fullmatch(item.name) for item in story_dir.iterdir() if item.is_file()):
            book_dirs.add(story_dir.parent)

    filtered = [item for item in book_dirs if "_legacy_story_dirs" not in item.parts]
    return sorted(filtered, key=lambda item: item.as_posix())


def migrate_library_layout(*, apply_changes: bool, create_backup: bool = True) -> dict[str, Any]:
    root = LIBRARY_ROOT.resolve()
    warnings: list[str] = []
    stats: dict[str, Any] = {
        "book_nodes_detected": 0,
        "stories_detected": 0,
        "stories_migrated": 0,
        "story_files_created": 0,
        "story_files_updated": 0,
        "pdf_copied": 0,
        "images_copied": 0,
        "legacy_dirs_archived": 0,
        "warnings": warnings,
    }

    for book_dir in _legacy_book_dirs(root):
        stats["book_nodes_detected"] += 1

        story_dirs = sorted(
            child
            for child in book_dir.iterdir()
            if child.is_dir() and STORY_DIR_RE.fullmatch(child.name)
        )

        processed_story_dirs: list[Path] = []
        for story_dir in story_dirs:
            story_id = story_dir.name
            pages = _collect_legacy_pages(story_dir, warnings)
            if not pages:
                continue

            stats["stories_detected"] += 1
            meta = _parse_legacy_meta(story_dir, story_id)
            rendered_story = _render_story_markdown(meta, pages)

            target_story_file = book_dir / f"{story_id}.md"
            existing_story = ""
            if target_story_file.exists():
                existing_story = read_text_with_fallback(target_story_file)

            if not target_story_file.exists():
                stats["story_files_created"] += 1
                stats["stories_migrated"] += 1
                if apply_changes:
                    target_story_file.write_text(rendered_story, encoding="utf-8")
            elif existing_story != rendered_story:
                stats["story_files_updated"] += 1
                stats["stories_migrated"] += 1
                if apply_changes:
                    target_story_file.write_text(rendered_story, encoding="utf-8")

            source_pdf = _story_pdf_source(story_dir)
            if source_pdf:
                target_pdf = book_dir / f"{story_id}.pdf"
                if not target_pdf.exists():
                    stats["pdf_copied"] += 1
                    if apply_changes:
                        shutil.copy2(source_pdf, target_pdf)

            image_dir = story_dir / "imagenes"
            if image_dir.exists() and image_dir.is_dir():
                fallback_index = 1
                for image_file in sorted(image_dir.iterdir(), key=lambda item: item.name.lower()):
                    if not image_file.is_file():
                        continue
                    if image_file.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                        continue
                    target_image_name, warning = _target_image_name(
                        story_id=story_id,
                        source_name=image_file.name,
                        fallback_index=fallback_index,
                    )
                    fallback_index += 1
                    if warning:
                        warnings.append(f"[{story_dir}] {warning}")

                    target_image = book_dir / target_image_name
                    if target_image.exists():
                        continue
                    stats["images_copied"] += 1
                    if apply_changes:
                        shutil.copy2(image_file, target_image)

            processed_story_dirs.append(story_dir)

        if not apply_changes or not create_backup:
            continue

        legacy_root = book_dir / "_legacy_story_dirs"
        legacy_root.mkdir(parents=True, exist_ok=True)
        for story_dir in processed_story_dirs:
            destination = legacy_root / story_dir.name
            if destination.exists():
                continue
            try:
                shutil.move(str(story_dir), str(destination))
                stats["legacy_dirs_archived"] += 1
            except PermissionError:
                warnings.append(
                    f"[{story_dir}] No se pudo archivar el directorio legacy por permisos."
                )

    stats["mode"] = "apply" if apply_changes else "dry-run"
    return stats
