from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from .config import DATA_ROOT
from .text_pages import parse_markdown_pages
from .utils import read_text_with_fallback, slugify

LEGACY_SOURCE_NAME = "origen_md.md"
LEGACY_BACKUP_NAME = "origen_md.legacy.md"
LEGACY_TEXTS_DIR_NAME = "textos"
PAGE_RAW_RE = re.compile(r"^\s*(\d+)\s*$")
CODE_RE = re.compile(r"^\d{2}$")


def _yaml_quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def _render_meta(titulo: str, slug: str, estado: str = "activo") -> str:
    lines = [
        "---",
        f"titulo: {_yaml_quote(titulo)}",
        f"slug: {_yaml_quote(slug)}",
        'prompt_portada: ""',
        'prompt_contraportada: ""',
        f"estado: {_yaml_quote(estado)}",
        "---",
        "",
    ]
    return "\n".join(lines)


def _slot_role(tipo_imagen: str) -> str:
    value = tipo_imagen.strip().lower()
    if value == "principal":
        return "principal"
    if value in {"referencia", "ancla"}:
        return "referencia"
    return "secundaria"


def _slot_name(role: str, index: int) -> str:
    if role == "principal" and index == 1:
        return "principal"
    if role == "principal":
        return f"principal-{index:02d}"
    if role == "referencia":
        return f"referencia-{index:02d}"
    return f"secundaria-{index:02d}"


def _normalize_prompt(entry: dict[str, Any]) -> str:
    value = (
        str(entry.get("prompt_final_literal", "")).strip()
        or str(entry.get("bloque_copy_paste", "")).strip()
        or str(entry.get("descripcion", "")).strip()
    )
    return " ".join(value.split())


def _load_prompt_map(book_dir: Path, warnings: list[str]) -> dict[str, dict[int, list[dict[str, str]]]]:
    prompt_file = book_dir / "prompts" / "era1_prompts_data.json"
    if not prompt_file.exists():
        return {}
    try:
        payload = json.loads(read_text_with_fallback(prompt_file))
    except json.JSONDecodeError as exc:
        warnings.append(f"[{prompt_file}] JSON inválido: {exc}")
        return {}

    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        warnings.append(f"[{prompt_file}] Campo 'entries' inválido.")
        return {}

    result: dict[str, dict[int, list[dict[str, str]]]] = {}
    counters: dict[tuple[str, int, str], int] = {}
    for raw in entries:
        if not isinstance(raw, dict):
            continue
        code = str(raw.get("bloque", "")).strip()
        if not CODE_RE.fullmatch(code):
            continue
        page_raw = str(raw.get("pagina", "")).strip()
        match = PAGE_RAW_RE.fullmatch(page_raw)
        if not match:
            continue
        page_num = int(match.group(1))
        if page_num <= 0:
            continue

        role = _slot_role(str(raw.get("tipo_imagen", "")))
        counter_key = (code, page_num, role)
        counters[counter_key] = counters.get(counter_key, 0) + 1
        slot = _slot_name(role, counters[counter_key])
        prompt = _normalize_prompt(raw)

        result.setdefault(code, {}).setdefault(page_num, []).append(
            {
                "slot": slot,
                "rol": role,
                "prompt": prompt,
            }
        )
    return result


def _render_page(page_num: int, contenido: str, slots: list[dict[str, str]]) -> str:
    lines = ["---", f"pagina: {page_num}"]
    if not slots:
        lines.append("imagenes: []")
    else:
        lines.append("imagenes:")
        for slot in slots:
            lines.append(f"  - slot: {slot['slot']}")
            lines.append(f"    rol: {slot['rol']}")
            lines.append(f"    prompt: {_yaml_quote(slot['prompt'])}")
            lines.append("    requisitos: []")
    lines.append("---")
    lines.append("")
    body = contenido.rstrip()
    if body:
        lines.append(body)
    lines.append("")
    return "\n".join(lines)


def _legacy_story_dirs(root: Path) -> list[Path]:
    stories: list[Path] = []
    for src in root.rglob(LEGACY_SOURCE_NAME):
        if src.parent.name != LEGACY_TEXTS_DIR_NAME:
            continue
        story_dir = src.parent.parent
        if story_dir not in stories:
            stories.append(story_dir)
    stories.sort(key=lambda p: p.as_posix())
    return stories


def migrate_library_layout(*, apply_changes: bool, create_backup: bool = True) -> dict[str, Any]:
    root = DATA_ROOT.resolve()
    warnings: list[str] = []
    stats = {
        "stories_detected": 0,
        "stories_migrated": 0,
        "meta_created": 0,
        "pages_created": 0,
        "pages_skipped": 0,
        "backups_created": 0,
        "pdf_copied": 0,
        "warnings": warnings,
    }

    prompt_map_cache: dict[Path, dict[str, dict[int, list[dict[str, str]]]]] = {}

    for story_dir in _legacy_story_dirs(root):
        stats["stories_detected"] += 1
        code = story_dir.name.strip()
        source_md = story_dir / LEGACY_TEXTS_DIR_NAME / LEGACY_SOURCE_NAME
        source_pdf = story_dir / LEGACY_TEXTS_DIR_NAME / "referencia_pdf.pdf"
        if not source_md.exists():
            warnings.append(f"[{story_dir}] Falta {LEGACY_SOURCE_NAME}.")
            continue

        story_warnings: list[str] = []
        markdown = read_text_with_fallback(source_md)
        pages, parse_warnings = parse_markdown_pages(markdown)
        story_warnings.extend(parse_warnings)
        if not pages:
            warnings.append(f"[{story_dir}] Sin páginas parseables en {LEGACY_SOURCE_NAME}.")
            continue

        book_dir = story_dir.parent
        if book_dir not in prompt_map_cache:
            prompt_map_cache[book_dir] = _load_prompt_map(book_dir, warnings)
        prompt_map = prompt_map_cache[book_dir]
        page_slots = prompt_map.get(code, {}) if CODE_RE.fullmatch(code) else {}

        meta_path = story_dir / "meta.md"
        created_meta_for_story = False
        if not meta_path.exists():
            titulo = f"Cuento {code}" if CODE_RE.fullmatch(code) else story_dir.name
            slug = slugify(story_dir.name)
            meta_text = _render_meta(titulo=titulo, slug=slug)
            if apply_changes:
                meta_path.write_text(meta_text, encoding="utf-8")
            stats["meta_created"] += 1
            created_meta_for_story = True

        created_for_story = 0
        for numero, contenido in sorted(pages.items()):
            page_path = story_dir / f"{numero:03d}.md"
            if page_path.exists():
                stats["pages_skipped"] += 1
                continue
            page_text = _render_page(numero, contenido, page_slots.get(numero, []))
            if apply_changes:
                page_path.write_text(page_text, encoding="utf-8")
            stats["pages_created"] += 1
            created_for_story += 1

        if source_pdf.exists():
            dst_pdf = story_dir / "referencias" / "referencia_pdf.pdf"
            if not dst_pdf.exists():
                if apply_changes:
                    dst_pdf.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_pdf, dst_pdf)
                stats["pdf_copied"] += 1

        backup_path = source_md.with_name(LEGACY_BACKUP_NAME)
        if create_backup and not backup_path.exists():
            if apply_changes:
                shutil.copy2(source_md, backup_path)
            stats["backups_created"] += 1

        for message in story_warnings:
            warnings.append(f"[{story_dir.relative_to(root).as_posix()}] {message}")

        if created_for_story > 0 or created_meta_for_story:
            stats["stories_migrated"] += 1

    stats["mode"] = "apply" if apply_changes else "dry-run"
    return stats
