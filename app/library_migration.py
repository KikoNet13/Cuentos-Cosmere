from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT
from .text_pages import parse_markdown_pages
from .utils import read_text_with_fallback, slugify

LEGACY_SOURCE_MD_NAME = "origen_md.md"
LEGACY_BACKUP_MD_NAME = "origen_md.legacy.md"
LEGACY_TEXTS_DIR_NAME = "textos"
LEGACY_PROMPT_JSON_NAME = "era1_prompts_data.json"
LEGACY_PROMPT_BACKUP_SUFFIX = ".legacy.json"

CANON_PDF_NAME = "referencia.pdf"

PAGE_RAW_PATTERN = re.compile(r"^\s*(\d+)\s*$")
STORY_CODE_PATTERN = re.compile(r"^\d{2}$")
ANCHOR_MARKER_START = "<!-- AUTO-ANCHORS:BEGIN -->"
ANCHOR_MARKER_END = "<!-- AUTO-ANCHORS:END -->"


def _yaml_quote(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def _render_meta(title: str, slug: str, status: str = "activo") -> str:
    lines = [
        "---",
        f"titulo: {_yaml_quote(title)}",
        f"slug: {_yaml_quote(slug)}",
        'prompt_portada: ""',
        'prompt_contraportada: ""',
        f"estado: {_yaml_quote(status)}",
        "---",
        "",
    ]
    return "\n".join(lines)


def _slot_role(image_type: str) -> str:
    normalized = image_type.strip().lower()
    if normalized == "principal":
        return "principal"
    if normalized in {"ancla", "referencia"}:
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


def _normalize_prompt_text(entry: dict[str, Any]) -> str:
    value = (
        str(entry.get("prompt_final_literal", "")).strip()
        or str(entry.get("bloque_copy_paste", "")).strip()
        or str(entry.get("descripcion", "")).strip()
    )
    return " ".join(value.split())


def _parse_page_number(raw_value: str) -> int | None:
    match = PAGE_RAW_PATTERN.fullmatch(raw_value.strip())
    if not match:
        return None
    value = int(match.group(1))
    return value if value > 0 else None


def _load_legacy_prompt_bundle(
    book_dir: Path,
    warnings: list[str],
) -> tuple[dict[str, dict[int, list[dict[str, str]]]], list[dict[str, str]], Path | None]:
    prompt_file = book_dir / "prompts" / LEGACY_PROMPT_JSON_NAME
    if not prompt_file.exists():
        return {}, [], None

    try:
        payload = json.loads(read_text_with_fallback(prompt_file))
    except json.JSONDecodeError as exc:
        warnings.append(f"[{prompt_file}] JSON inválido: {exc}")
        return {}, [], prompt_file

    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        warnings.append(f"[{prompt_file}] Campo 'entries' inválido.")
        return {}, [], prompt_file

    story_page_slots: dict[str, dict[int, list[dict[str, str]]]] = {}
    role_counter: dict[tuple[str, int, str], int] = {}
    anchor_entries: dict[str, dict[str, str]] = {}

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        story_code = str(entry.get("bloque", "")).strip()
        if not STORY_CODE_PATTERN.fullmatch(story_code):
            continue

        page_raw = str(entry.get("pagina", "")).strip()
        page_number = _parse_page_number(page_raw)
        image_type = str(entry.get("tipo_imagen", "")).strip()
        role = _slot_role(image_type)
        prompt_text = _normalize_prompt_text(entry)

        if page_number is not None:
            counter_key = (story_code, page_number, role)
            role_counter[counter_key] = role_counter.get(counter_key, 0) + 1
            slot = _slot_name(role, role_counter[counter_key])
            story_page_slots.setdefault(story_code, {}).setdefault(page_number, []).append(
                {
                    "slot": slot,
                    "rol": role,
                    "prompt": prompt_text,
                }
            )
            continue

        if role != "referencia" and image_type.strip().lower() != "ancla":
            continue

        anchor_id = str(entry.get("id_prompt", "")).strip()
        if not anchor_id:
            continue

        anchor_entries[anchor_id] = {
            "id": anchor_id,
            "nombre": str(entry.get("generar_una_imagen_de", "")).strip() or anchor_id,
            "descripcion": str(entry.get("descripcion", "")).strip(),
            "prompt": prompt_text,
            "imagen": str(entry.get("imagen_rel_path", "")).strip().replace("\\", "/"),
            "estado": str(entry.get("estado", "activo")).strip() or "activo",
        }

    return story_page_slots, list(anchor_entries.values()), prompt_file


def _render_slots_block(slots: list[dict[str, str]]) -> list[str]:
    lines = ["imagenes:"]
    for slot in slots:
        lines.append(f"  - slot: {slot['slot']}")
        lines.append(f"    rol: {slot['rol']}")
        lines.append(f"    prompt: {_yaml_quote(slot['prompt'])}")
        lines.append("    requisitos: []")
    return lines


def _render_page(page_number: int, content: str, slots: list[dict[str, str]]) -> str:
    lines = ["---", f"pagina: {page_number}"]
    if slots:
        lines.extend(_render_slots_block(slots))
    else:
        lines.append("imagenes: []")
    lines.append("---")
    lines.append("")

    body = content.rstrip()
    if body:
        lines.append(body)
    lines.append("")
    return "\n".join(lines)


def _inject_slots_if_placeholder(existing_text: str, slots: list[dict[str, str]]) -> tuple[str, bool]:
    if not slots:
        return existing_text, False

    lines = existing_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return existing_text, False

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return existing_text, False

    fm_lines = lines[1:end_index]
    placeholder_index = None
    for i, line in enumerate(fm_lines):
        if line.strip().startswith("imagenes:") and line.strip() != "imagenes: []":
            return existing_text, False
        if line.strip() == "imagenes: []":
            placeholder_index = i

    if placeholder_index is None:
        return existing_text, False

    new_frontmatter = list(fm_lines[:placeholder_index])
    new_frontmatter.extend(_render_slots_block(slots))
    new_frontmatter.extend(fm_lines[placeholder_index + 1 :])

    rebuilt_lines = ["---"] + new_frontmatter + ["---"] + lines[end_index + 1 :]
    return "\n".join(rebuilt_lines).rstrip("\n") + "\n", True


def _legacy_story_dirs(root: Path) -> list[Path]:
    story_dirs: list[Path] = []
    for source_md in root.rglob(LEGACY_SOURCE_MD_NAME):
        if source_md.parent.name != LEGACY_TEXTS_DIR_NAME:
            continue
        story_dir = source_md.parent.parent
        if story_dir not in story_dirs:
            story_dirs.append(story_dir)
    story_dirs.sort(key=lambda item: item.as_posix())
    return story_dirs


def _find_obsolete_reference_pdfs(texts_dir: Path) -> list[Path]:
    obsolete_files: list[Path] = []
    for candidate in texts_dir.glob("referencia*.pdf"):
        if candidate.name == CANON_PDF_NAME:
            continue
        obsolete_files.append(candidate)
    obsolete_files.sort(key=lambda item: item.name)
    return obsolete_files


def _render_anchor_guide(anchor_items: list[dict[str, str]]) -> str:
    lines = [
        "# Referencias de anclas de la saga",
        "",
        "Documento canónico de referencia visual de anclas.",
        "",
        ANCHOR_MARKER_START,
    ]

    if not anchor_items:
        lines.extend(["", "Sin anclas definidas."])
    else:
        for item in sorted(anchor_items, key=lambda value: value["id"]):
            lines.extend(
                [
                    "",
                    f"## {item['id']}",
                    f"- Nombre: {item['nombre']}",
                    f"- Estado: {item['estado']}",
                ]
            )
            if item["descripcion"]:
                lines.append(f"- Descripción: {item['descripcion']}")
            if item["prompt"]:
                lines.append(f"- Prompt: {item['prompt']}")
            if item["imagen"]:
                lines.append(f"- Imagen de referencia: `{item['imagen']}`")

    lines.extend(["", ANCHOR_MARKER_END, ""])
    return "\n".join(lines)


def _upsert_anchor_guide(
    saga_dir: Path,
    anchor_items: list[dict[str, str]],
    apply_changes: bool,
) -> bool:
    guide_path = saga_dir / "anclas.md"
    generated = _render_anchor_guide(anchor_items)

    if not guide_path.exists():
        if apply_changes:
            guide_path.write_text(generated, encoding="utf-8")
        return True

    existing = read_text_with_fallback(guide_path)
    if ANCHOR_MARKER_START in existing and ANCHOR_MARKER_END in existing:
        before = existing.split(ANCHOR_MARKER_START, 1)[0].rstrip()
        after = existing.split(ANCHOR_MARKER_END, 1)[1].lstrip("\n")
        managed = generated.split(ANCHOR_MARKER_START, 1)[1]
        merged = f"{before}\n\n{ANCHOR_MARKER_START}{managed}"
        if after:
            merged = merged.rstrip("\n") + "\n\n" + after
        merged = merged.rstrip("\n") + "\n"
        if apply_changes and merged != existing:
            guide_path.write_text(merged, encoding="utf-8")
            return True
        return False

    merged = existing.rstrip("\n") + "\n\n" + generated
    if apply_changes and merged != existing:
        guide_path.write_text(merged, encoding="utf-8")
        return True
    return False


def _retire_prompt_json(
    prompt_file: Path,
    create_backup: bool,
    apply_changes: bool,
    warnings: list[str],
) -> bool:
    if not prompt_file.exists():
        return False

    if not apply_changes:
        return True

    try:
        if create_backup:
            backup_name = prompt_file.name.replace(".json", LEGACY_PROMPT_BACKUP_SUFFIX)
            backup_path = prompt_file.with_name(backup_name)
            if backup_path.exists():
                prompt_file.unlink()
            else:
                shutil.move(prompt_file, backup_path)
        else:
            prompt_file.unlink()
        return True
    except OSError as exc:
        warnings.append(f"[{prompt_file}] No se pudo retirar JSON legacy: {exc}")
        return False


def migrate_library_layout(*, apply_changes: bool, create_backup: bool = True) -> dict[str, Any]:
    root = LIBRARY_ROOT.resolve()
    warnings: list[str] = []
    stats = {
        "stories_detected": 0,
        "stories_migrated": 0,
        "meta_created": 0,
        "pages_created": 0,
        "pages_updated": 0,
        "pages_skipped": 0,
        "md_backups_created": 0,
        "pdf_copied": 0,
        "anchors_guide_updated": 0,
        "anchor_entries": 0,
        "legacy_prompt_retired": 0,
        "warnings": warnings,
    }

    prompt_cache: dict[Path, tuple[dict[str, dict[int, list[dict[str, str]]]], list[dict[str, str]], Path | None]] = {}
    saga_anchor_map: dict[Path, dict[str, dict[str, str]]] = {}
    prompt_files_seen: set[Path] = set()

    for story_dir in _legacy_story_dirs(root):
        stats["stories_detected"] += 1
        story_code = story_dir.name.strip()
        legacy_texts_dir = story_dir / LEGACY_TEXTS_DIR_NAME

        source_md = legacy_texts_dir / LEGACY_SOURCE_MD_NAME
        source_pdf = legacy_texts_dir / CANON_PDF_NAME
        obsolete_pdfs = _find_obsolete_reference_pdfs(legacy_texts_dir)

        if obsolete_pdfs:
            for obsolete_pdf in obsolete_pdfs:
                warnings.append(
                    f"[{story_dir}] Archivo obsoleto detectado: {obsolete_pdf.name}."
                )
            if source_pdf.exists():
                warnings.append(f"[{story_dir}] Conflicto de PDF; se usa {CANON_PDF_NAME}.")

        if not source_md.exists():
            warnings.append(f"[{story_dir}] Falta {LEGACY_SOURCE_MD_NAME}.")
            continue

        markdown = read_text_with_fallback(source_md)
        pages, parse_warnings = parse_markdown_pages(markdown)
        warnings.extend(
            f"[{story_dir.relative_to(root).as_posix()}] {item}" for item in parse_warnings
        )
        if not pages:
            warnings.append(
                f"[{story_dir}] Sin páginas parseables en {LEGACY_SOURCE_MD_NAME}."
            )
            continue

        book_dir = story_dir.parent
        if book_dir not in prompt_cache:
            prompt_cache[book_dir] = _load_legacy_prompt_bundle(book_dir, warnings)
        page_slot_map, book_anchor_entries, prompt_file = prompt_cache[book_dir]
        if prompt_file:
            prompt_files_seen.add(prompt_file)

        saga_dir = book_dir.parent
        saga_anchor_map.setdefault(saga_dir, {})
        for anchor_entry in book_anchor_entries:
            saga_anchor_map[saga_dir][anchor_entry["id"]] = anchor_entry

        story_slots = page_slot_map.get(story_code, {}) if STORY_CODE_PATTERN.fullmatch(story_code) else {}

        meta_path = story_dir / "meta.md"
        created_meta = False
        if not meta_path.exists():
            story_title = f"Cuento {story_code}" if STORY_CODE_PATTERN.fullmatch(story_code) else story_dir.name
            story_slug = slugify(story_dir.name)
            if apply_changes:
                meta_path.write_text(
                    _render_meta(title=story_title, slug=story_slug),
                    encoding="utf-8",
                )
            stats["meta_created"] += 1
            created_meta = True

        created_pages = 0
        updated_pages = 0
        for page_number, content in sorted(pages.items()):
            page_path = story_dir / f"{page_number:03d}.md"
            generated_slots = story_slots.get(page_number, [])

            if page_path.exists():
                if generated_slots:
                    existing = read_text_with_fallback(page_path)
                    injected_text, changed = _inject_slots_if_placeholder(existing, generated_slots)
                    if changed:
                        if apply_changes:
                            page_path.write_text(injected_text, encoding="utf-8")
                        stats["pages_updated"] += 1
                        updated_pages += 1
                    else:
                        stats["pages_skipped"] += 1
                else:
                    stats["pages_skipped"] += 1
                continue

            page_text = _render_page(page_number=page_number, content=content, slots=generated_slots)
            if apply_changes:
                page_path.write_text(page_text, encoding="utf-8")
            stats["pages_created"] += 1
            created_pages += 1

        if source_pdf.exists():
            destination_pdf = story_dir / "referencias" / CANON_PDF_NAME
            if not destination_pdf.exists():
                if apply_changes:
                    destination_pdf.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_pdf, destination_pdf)
                stats["pdf_copied"] += 1

        backup_md = source_md.with_name(LEGACY_BACKUP_MD_NAME)
        if create_backup and not backup_md.exists():
            if apply_changes:
                shutil.copy2(source_md, backup_md)
            stats["md_backups_created"] += 1

        if created_meta or created_pages > 0 or updated_pages > 0:
            stats["stories_migrated"] += 1

    for saga_dir, anchor_items in saga_anchor_map.items():
        changed = _upsert_anchor_guide(
            saga_dir=saga_dir,
            anchor_items=list(anchor_items.values()),
            apply_changes=apply_changes,
        )
        if changed:
            stats["anchors_guide_updated"] += 1
        stats["anchor_entries"] += len(anchor_items)

    for prompt_file in sorted(prompt_files_seen):
        retired = _retire_prompt_json(
            prompt_file=prompt_file,
            create_backup=create_backup,
            apply_changes=apply_changes,
            warnings=warnings,
        )
        if retired:
            stats["legacy_prompt_retired"] += 1

    stats["mode"] = "apply" if apply_changes else "dry-run"
    return stats
