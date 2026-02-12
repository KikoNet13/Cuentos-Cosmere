from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT

PAGE_HEADER_RE = re.compile(r"(?im)^##\s*P(?:a|á)gina\s+(\d{1,2})\s*$")
TITLE_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
MOJIBAKE_MARKERS = ("Ã", "Â", "â€", "â€™", "â€œ", "â€\x9d")
ANCHOR_SECTION_RE = re.compile(r"(?im)^##\s+(.+?)\s*$")
ANCHOR_NAME_RE = re.compile(r"(?im)^\s*-\s*Nombre\s*:\s*(.+?)\s*$")
ANCHOR_IMAGE_RE = re.compile(r"(?im)^\s*-\s*Imagen de referencia\s*:\s*`?([^`\n]+?)`?\s*$")


@dataclass
class NotebookPage:
    page_number: int
    text: str
    image_prompt: str


@dataclass
class AnchorRef:
    anchor_id: str
    name: str
    image_ref: str
    tokens: set[str]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_compact() -> str:
    return _utc_now().strftime("%Y%m%d-%H%M%S")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_for_match(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9\s_-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _marker_count(text: str) -> int:
    return sum(text.count(marker) for marker in MOJIBAKE_MARKERS)


def _repair_mojibake(text: str) -> str:
    try:
        repaired = text.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return text

    if _marker_count(repaired) < _marker_count(text):
        return repaired
    return text


def _extract_code_block(source: str, label: str) -> str:
    pattern = re.compile(
        rf"(?is){re.escape(label)}\s*:\s*```(?:text|txt|markdown|md)?\s*(.*?)\s*```"
    )
    match = pattern.search(source)
    return match.group(1).strip() if match else ""


def _parse_notebook_markdown(raw_text: str) -> tuple[str, str, list[NotebookPage], list[str]]:
    warnings: list[str] = []
    title_match = TITLE_RE.search(raw_text)
    title = title_match.group(1).strip() if title_match else "Cuento sin título"

    page_matches = list(PAGE_HEADER_RE.finditer(raw_text))
    portada_region_end = page_matches[0].start() if page_matches else len(raw_text)
    portada_region = raw_text[:portada_region_end]
    portada_prompt = _extract_code_block(portada_region, "Portada")

    pages: list[NotebookPage] = []
    if not page_matches:
        warnings.append("No se detectaron secciones '## Página NN'.")
        return title, portada_prompt, pages, warnings

    seen_numbers: set[int] = set()
    for index, match in enumerate(page_matches):
        page_number = int(match.group(1))
        start = match.end()
        end = page_matches[index + 1].start() if index + 1 < len(page_matches) else len(raw_text)
        body = raw_text[start:end]

        text_block = _extract_code_block(body, "Texto")
        image_block = _extract_code_block(body, "Imagen")

        if not text_block:
            warnings.append(f"Página {page_number:02d}: bloque 'Texto' ausente o vacío.")
        if not image_block:
            warnings.append(f"Página {page_number:02d}: bloque 'Imagen' ausente o vacío.")

        if page_number in seen_numbers:
            warnings.append(f"Página {page_number:02d} repetida; se conserva la última aparición.")
            pages = [item for item in pages if item.page_number != page_number]

        seen_numbers.add(page_number)
        pages.append(
            NotebookPage(
                page_number=page_number,
                text=text_block,
                image_prompt=image_block,
            )
        )

    pages.sort(key=lambda item: item.page_number)
    return title, portada_prompt, pages, warnings


def _parse_anchor_refs(book_dir: Path) -> list[AnchorRef]:
    anchor_file = book_dir / "anclas.md"
    if not anchor_file.exists():
        return []

    raw_text = anchor_file.read_text(encoding="utf-8", errors="replace")
    sections = list(ANCHOR_SECTION_RE.finditer(raw_text))
    refs: list[AnchorRef] = []

    for index, match in enumerate(sections):
        anchor_id = match.group(1).strip()
        start = match.end()
        end = sections[index + 1].start() if index + 1 < len(sections) else len(raw_text)
        body = raw_text[start:end]

        name_match = ANCHOR_NAME_RE.search(body)
        name = name_match.group(1).strip() if name_match else anchor_id

        image_match = ANCHOR_IMAGE_RE.search(body)
        image_ref = image_match.group(1).strip() if image_match else f"anclas/{anchor_id.lower()}.png"

        tokens = {
            _normalize_for_match(anchor_id),
            _normalize_for_match(name),
        }
        tokens = {item for item in tokens if item and len(item) >= 3}

        refs.append(
            AnchorRef(
                anchor_id=anchor_id,
                name=name,
                image_ref=image_ref,
                tokens=tokens,
            )
        )

    return refs


def _detect_requirements(page: NotebookPage, anchors: list[AnchorRef]) -> list[dict[str, str]]:
    merged_text = _normalize_for_match(f"{page.text}\n{page.image_prompt}")
    detected: list[dict[str, str]] = []

    for anchor in anchors:
        if any(token in merged_text for token in anchor.tokens):
            detected.append({"tipo": "imagen", "ref": anchor.image_ref})

    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in detected:
        key = (item["tipo"], item["ref"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    return unique


def _render_requirements_yaml(requirements: list[dict[str, str]]) -> str:
    if not requirements:
        return "[]"

    lines: list[str] = []
    for requirement in requirements:
        lines.append(f"- tipo: {requirement['tipo']}")
        lines.append(f"  ref: {requirement['ref']}")
    return "\n".join(lines)


def _render_story_markdown(
    *,
    title: str,
    portada_prompt: str,
    pages: list[NotebookPage],
    page_requirements: dict[int, list[dict[str, str]]],
) -> str:
    lines: list[str] = [
        f"# {title}",
        "",
        "## Meta",
        "- estado: activo",
        f"- prompt_portada: {portada_prompt}",
        "- prompt_contraportada:",
        "- notas:",
        "",
    ]

    for page in pages:
        requirements = page_requirements.get(page.page_number, [])
        lines.extend(
            [
                f"## Página {page.page_number:02d}",
                "",
                "### Texto",
                page.text.strip(),
                "",
                "### Prompts",
                "",
                "#### principal",
                "```text",
                page.image_prompt.strip(),
                "```",
                "",
                "##### Requisitos",
                "```yaml",
                _render_requirements_yaml(requirements),
                "```",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _build_review_text(
    *,
    title: str,
    story_id: str,
    book_rel_path: str,
    pages: list[NotebookPage],
    warnings: list[str],
    page_requirements: dict[int, list[dict[str, str]]],
) -> str:
    lines = [
        "# Revisión de propuesta",
        "",
        f"- cuento: {story_id}",
        f"- libro: {book_rel_path}",
        f"- título detectado: {title}",
        f"- páginas detectadas: {len(pages)}",
        "",
        "## Warnings",
    ]

    if warnings:
        lines.extend(f"- {item}" for item in warnings)
    else:
        lines.append("- sin warnings")

    lines.append("")
    lines.append("## Requisitos detectados")

    for page in pages:
        lines.append(f"### Página {page.page_number:02d}")
        requirements = page_requirements.get(page.page_number, [])
        if not requirements:
            lines.append("- sin referencias automáticas")
            continue
        for requirement in requirements:
            lines.append(f"- tipo: {requirement['tipo']} | ref: {requirement['ref']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def inbox_parse(*, input_path: str, book_rel_path: str, story_id: str) -> dict[str, Any]:
    normalized_story_id = story_id.strip()
    if not re.fullmatch(r"\d{2}", normalized_story_id):
        raise ValueError("story_id debe tener formato de 2 dígitos (NN).")

    normalized_book_rel = book_rel_path.strip().replace("\\", "/").strip("/")
    if not normalized_book_rel:
        raise ValueError("book_rel_path no puede estar vacío.")

    source_file = Path(input_path).resolve()
    if not source_file.exists() or not source_file.is_file():
        raise FileNotFoundError(f"No existe el archivo de entrada: {source_file}")

    raw_input = source_file.read_text(encoding="utf-8", errors="replace")
    repaired_input = _repair_mojibake(raw_input)

    title, portada_prompt, pages, warnings = _parse_notebook_markdown(repaired_input)

    book_dir = (LIBRARY_ROOT / normalized_book_rel).resolve()
    anchors = _parse_anchor_refs(book_dir)
    page_requirements = {
        page.page_number: _detect_requirements(page, anchors)
        for page in pages
    }

    batch_id = f"{_utc_now_compact()}-{normalized_story_id}"
    batch_dir = LIBRARY_ROOT / "_inbox" / batch_id
    proposal_dir = batch_dir / "proposal"
    proposal_dir.mkdir(parents=True, exist_ok=True)

    proposal_file = proposal_dir / f"{normalized_story_id}.md"
    proposal_markdown = _render_story_markdown(
        title=title,
        portada_prompt=portada_prompt,
        pages=pages,
        page_requirements=page_requirements,
    )

    input_copy = batch_dir / "input.md"
    normalized_copy = batch_dir / "normalized.md"
    review_file = batch_dir / "review.md"
    manifest_file = batch_dir / "manifest.json"

    input_copy.write_text(raw_input, encoding="utf-8")
    normalized_copy.write_text(repaired_input, encoding="utf-8")
    proposal_file.write_text(proposal_markdown, encoding="utf-8")
    review_file.write_text(
        _build_review_text(
            title=title,
            story_id=normalized_story_id,
            book_rel_path=normalized_book_rel,
            pages=pages,
            warnings=warnings,
            page_requirements=page_requirements,
        ),
        encoding="utf-8",
    )

    manifest = {
        "batch_id": batch_id,
        "status": "proposed",
        "story_id": normalized_story_id,
        "book_rel_path": normalized_book_rel,
        "input_source": str(source_file),
        "input_file": str(input_copy.relative_to(LIBRARY_ROOT)).replace("\\", "/"),
        "normalized_file": str(normalized_copy.relative_to(LIBRARY_ROOT)).replace("\\", "/"),
        "proposal_file": str(proposal_file.relative_to(LIBRARY_ROOT)).replace("\\", "/"),
        "review_file": str(review_file.relative_to(LIBRARY_ROOT)).replace("\\", "/"),
        "created_at": _utc_now().isoformat(),
        "warnings": warnings,
        "hashes": {
            "input_sha256": _sha256_text(raw_input),
            "normalized_sha256": _sha256_text(repaired_input),
            "proposal_sha256": _sha256_text(proposal_markdown),
        },
    }
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "batch_id": batch_id,
        "book_rel_path": normalized_book_rel,
        "story_id": normalized_story_id,
        "title": title,
        "pages_detected": len(pages),
        "warnings": warnings,
        "manifest": str(manifest_file.relative_to(LIBRARY_ROOT)).replace("\\", "/"),
        "proposal": str(proposal_file.relative_to(LIBRARY_ROOT)).replace("\\", "/"),
    }


def inbox_apply(*, batch_id: str, approve: bool, force: bool = False) -> dict[str, Any]:
    if not approve:
        raise ValueError("Debes usar --approve para aplicar una propuesta.")

    normalized_batch_id = batch_id.strip()
    if not normalized_batch_id:
        raise ValueError("batch_id no puede estar vacío.")

    batch_dir = LIBRARY_ROOT / "_inbox" / normalized_batch_id
    manifest_file = batch_dir / "manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"No existe manifest para el batch: {normalized_batch_id}")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8", errors="replace"))
    status = str(manifest.get("status", ""))
    if status != "proposed" and not force:
        raise ValueError(f"El batch {normalized_batch_id} no está en estado proposed (actual: {status}).")

    story_id = str(manifest.get("story_id", "")).strip()
    book_rel_path = str(manifest.get("book_rel_path", "")).strip().replace("\\", "/").strip("/")
    proposal_rel = str(manifest.get("proposal_file", "")).strip().replace("\\", "/")
    if not re.fullmatch(r"\d{2}", story_id):
        raise ValueError("manifest inválido: story_id debe tener formato NN.")
    if not book_rel_path or not proposal_rel:
        raise ValueError("manifest inválido: faltan book_rel_path/proposal_file.")

    proposal_file = LIBRARY_ROOT / proposal_rel
    if not proposal_file.exists():
        raise FileNotFoundError(f"No existe archivo de propuesta: {proposal_file}")

    target_dir = LIBRARY_ROOT / book_rel_path
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / f"{story_id}.md"

    backed_up = False
    if target_file.exists():
        backup_root = LIBRARY_ROOT / "_backups" / _utc_now_compact() / book_rel_path
        backup_root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target_file, backup_root / target_file.name)
        backed_up = True

    shutil.copy2(proposal_file, target_file)

    manifest["status"] = "applied"
    manifest["applied_at"] = _utc_now().isoformat()
    manifest["applied_target"] = str(target_file.relative_to(LIBRARY_ROOT)).replace("\\", "/")
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "batch_id": normalized_batch_id,
        "story_id": story_id,
        "book_rel_path": book_rel_path,
        "target": str(target_file.relative_to(LIBRARY_ROOT)).replace("\\", "/"),
        "backup_created": backed_up,
        "warnings": [],
    }
