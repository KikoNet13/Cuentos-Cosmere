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

PAGE_HEADER_RE = re.compile(r"(?im)^##\s*P(?:a|\u00e1)gina\s+(\d{1,2})\s*$")
TITLE_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
MOJIBAKE_MARKERS = ("Ãƒ", "Ã‚", "Ã¢â‚¬", "Ã¢â‚¬â„¢", "Ã¢â‚¬Å“", "Ã¢â‚¬\x9d")
ANCHOR_SECTION_RE = re.compile(r"(?im)^##\s+(.+?)\s*$")
ANCHOR_NAME_RE = re.compile(r"(?im)^\s*-\s*Nombre\s*:\s*(.+?)\s*$")
ANCHOR_IMAGE_RE = re.compile(r"(?im)^\s*-\s*Imagen de referencia\s*:\s*`?([^`\n]+?)`?\s*$")
H2_SECTION_RE = re.compile(r"(?im)^##\s+(.+?)\s*$")

GLOSSARY_COLUMNS = ["termino", "canonico", "permitidas", "prohibidas", "notas"]

AI_REVIEW_STATUSES = {"pending", "approved", "blocked", "approved_with_warnings"}
AI_REVIEW_MODE = "codex_chat_manual"
AI_FINDING_SEVERITIES = {"critical", "major", "minor", "info"}
AI_FINDING_CATEGORIES = {"canon", "terminology", "continuity_visual", "style_tone"}
AI_FINDING_STATES = {"open", "resolved", "waived"}


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


@dataclass
class GlossaryTerm:
    term: str
    canonical: str
    allowed: list[str]
    prohibited: list[str]
    notes: str
    source_meta_file: str
    source_node: str


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


def _library_rel_path(path: Path) -> str:
    try:
        rel = path.resolve().relative_to(LIBRARY_ROOT.resolve()).as_posix()
    except ValueError:
        rel = path.resolve().as_posix()
    return "" if rel == "." else rel


def _truncate_text(text: str, limit: int) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: max(limit - 3, 0)].rstrip() + "..."


def _parse_notebook_markdown(raw_text: str) -> tuple[str, str, list[NotebookPage], list[str]]:
    warnings: list[str] = []
    title_match = TITLE_RE.search(raw_text)
    title = title_match.group(1).strip() if title_match else "Cuento sin titulo"

    page_matches = list(PAGE_HEADER_RE.finditer(raw_text))
    portada_region_end = page_matches[0].start() if page_matches else len(raw_text)
    portada_region = raw_text[:portada_region_end]
    portada_prompt = _extract_code_block(portada_region, "Portada")

    pages: list[NotebookPage] = []
    if not page_matches:
        warnings.append("No se detectaron secciones '## Pagina NN'.")
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
            warnings.append(f"Pagina {page_number:02d}: bloque 'Texto' ausente o vacio.")
        if not image_block:
            warnings.append(f"Pagina {page_number:02d}: bloque 'Imagen' ausente o vacio.")

        if page_number in seen_numbers:
            warnings.append(f"Pagina {page_number:02d} repetida; se conserva la ultima aparicion.")
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
                f"## Pagina {page.page_number:02d}",
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
        "# Revision de propuesta",
        "",
        f"- cuento: {story_id}",
        f"- libro: {book_rel_path}",
        f"- titulo detectado: {title}",
        f"- paginas detectadas: {len(pages)}",
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
        lines.append(f"### Pagina {page.page_number:02d}")
        requirements = page_requirements.get(page.page_number, [])
        if not requirements:
            lines.append("- sin referencias automaticas")
            continue
        for requirement in requirements:
            lines.append(f"- tipo: {requirement['tipo']} | ref: {requirement['ref']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _split_h2_sections(raw_text: str) -> list[tuple[str, str]]:
    matches = list(H2_SECTION_RE.finditer(raw_text))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw_text)
        sections.append((match.group(1).strip(), raw_text[start:end].strip("\n")))
    return sections


def _parse_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return []
    return [item.strip() for item in stripped.strip("|").split("|")]


def _is_table_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(bool(re.fullmatch(r"[:\- ]+", cell)) for cell in cells)


def _split_glossary_cell(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def _parse_glossary_terms_from_meta(
    raw_meta: str,
    *,
    source_meta_file: str,
    source_node: str,
) -> tuple[list[GlossaryTerm], bool, list[str]]:
    warnings: list[str] = []
    glossary_section = ""

    for section_title, section_body in _split_h2_sections(raw_meta):
        if _normalize_for_match(section_title) == "glosario":
            glossary_section = section_body
            break

    if not glossary_section:
        return [], False, warnings

    table_lines = [line.strip() for line in glossary_section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        warnings.append("La seccion '## Glosario' no contiene tabla Markdown valida.")
        return [], True, warnings

    header_cells = _parse_markdown_table_row(table_lines[0])
    if not header_cells:
        warnings.append("No se pudo leer cabecera de la tabla de glosario.")
        return [], True, warnings

    header_normalized = [_normalize_for_match(item).replace(" ", "") for item in header_cells]
    missing_columns = [name for name in GLOSSARY_COLUMNS if name not in header_normalized]
    if missing_columns:
        warnings.append(
            "Tabla de glosario invalida: faltan columnas requeridas "
            + ", ".join(missing_columns)
            + "."
        )
        return [], True, warnings

    index_by_column = {name: header_normalized.index(name) for name in GLOSSARY_COLUMNS}

    data_lines = table_lines[1:]
    if data_lines and _is_table_separator_row(_parse_markdown_table_row(data_lines[0])):
        data_lines = data_lines[1:]

    terms: list[GlossaryTerm] = []
    for row_index, line in enumerate(data_lines, start=1):
        cells = _parse_markdown_table_row(line)
        if not cells:
            continue

        if len(cells) < len(header_cells):
            warnings.append(
                f"Fila {row_index} de glosario incompleta en {source_meta_file}; se omite."
            )
            continue

        term = cells[index_by_column["termino"]].strip()
        canonical = cells[index_by_column["canonico"]].strip() or term
        allowed = _split_glossary_cell(cells[index_by_column["permitidas"]])
        prohibited = _split_glossary_cell(cells[index_by_column["prohibidas"]])
        notes = cells[index_by_column["notas"]].strip()

        if not term:
            warnings.append(
                f"Fila {row_index} de glosario sin termino en {source_meta_file}; se omite."
            )
            continue

        terms.append(
            GlossaryTerm(
                term=term,
                canonical=canonical,
                allowed=allowed,
                prohibited=prohibited,
                notes=notes,
                source_meta_file=source_meta_file,
                source_node=source_node,
            )
        )

    return terms, True, warnings


def _ancestor_nodes(book_rel_path: str) -> list[Path]:
    root = LIBRARY_ROOT.resolve()
    parts = [part for part in book_rel_path.split("/") if part]
    nodes = [root]
    for index in range(len(parts)):
        nodes.append((root / Path(*parts[: index + 1])).resolve())
    return nodes


def _load_hierarchical_glossary(book_rel_path: str) -> tuple[list[GlossaryTerm], list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    sources: list[dict[str, Any]] = []
    merged_terms: dict[str, GlossaryTerm] = {}

    for node_dir in _ancestor_nodes(book_rel_path):
        node_rel = _library_rel_path(node_dir) or "/"
        meta_file = node_dir / "meta.md"
        source_entry: dict[str, Any] = {
            "node_rel_path": node_rel,
            "meta_file": "",
            "has_meta": False,
            "has_glossary": False,
            "terms": 0,
        }

        if not meta_file.exists():
            warnings.append(f"No existe meta.md para glosario en nodo '{node_rel}'.")
            sources.append(source_entry)
            continue

        source_entry["has_meta"] = True
        source_entry["meta_file"] = _library_rel_path(meta_file)

        raw_meta = meta_file.read_text(encoding="utf-8", errors="replace")
        terms, has_glossary, parse_warnings = _parse_glossary_terms_from_meta(
            raw_meta,
            source_meta_file=_library_rel_path(meta_file),
            source_node=node_rel,
        )

        source_entry["has_glossary"] = has_glossary
        source_entry["terms"] = len(terms)
        sources.append(source_entry)

        if not has_glossary:
            warnings.append(f"meta.md en '{node_rel}' no contiene seccion ## Glosario.")

        for warning in parse_warnings:
            warnings.append(f"[{node_rel}] {warning}")

        for term in terms:
            key = _normalize_for_match(term.term)
            if not key:
                continue
            merged_terms[key] = term

    return list(merged_terms.values()), sources, warnings


def _extract_pdf_text(pdf_file: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []

    try:
        from pypdf import PdfReader
    except Exception:
        warnings.append("No se pudo importar pypdf para extraer texto de PDF.")
        return "", warnings

    try:
        reader = PdfReader(str(pdf_file))
    except Exception as exc:
        warnings.append(f"No se pudo abrir PDF de referencia '{_library_rel_path(pdf_file)}': {exc}")
        return "", warnings

    chunks: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:
            warnings.append(
                f"No se pudo extraer texto de pagina {page_number} en '{_library_rel_path(pdf_file)}': {exc}"
            )
            continue
        text = text.strip()
        if text:
            chunks.append(text)

    merged = "\n\n".join(chunks).strip()
    if not merged:
        warnings.append(f"El PDF '{_library_rel_path(pdf_file)}' no devolvio texto extraible.")

    return merged, warnings


def _collect_canon_context(book_dir: Path, story_id: str) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    canon_stories: list[dict[str, Any]] = []

    if not book_dir.exists() or not book_dir.is_dir():
        warnings.append(f"No existe directorio de libro para contexto canonico: {_library_rel_path(book_dir)}")
        return {
            "book_rel_path": _library_rel_path(book_dir),
            "stories": [],
            "reference_pdf": {
                "exists": False,
                "path": _library_rel_path(book_dir / f"{story_id}.pdf"),
                "sha256": "",
                "text_excerpt": "",
                "text_chars": 0,
            },
            "anchors": [],
        }, warnings

    for story_file in sorted(book_dir.glob("[0-9][0-9].md")):
        raw_story = story_file.read_text(encoding="utf-8", errors="replace")
        title_match = TITLE_RE.search(raw_story)
        canon_stories.append(
            {
                "story_id": story_file.stem,
                "path": _library_rel_path(story_file),
                "title": title_match.group(1).strip() if title_match else f"Cuento {story_file.stem}",
                "pages_detected": len(PAGE_HEADER_RE.findall(raw_story)),
                "sha256": _sha256_text(raw_story),
                "content_excerpt": _truncate_text(raw_story, 12000),
            }
        )

    reference_pdf = book_dir / f"{story_id}.pdf"
    pdf_text = ""
    pdf_warnings: list[str] = []
    if reference_pdf.exists():
        pdf_text, pdf_warnings = _extract_pdf_text(reference_pdf)
        warnings.extend(pdf_warnings)
    else:
        warnings.append(f"No existe PDF de referencia esperado: {_library_rel_path(reference_pdf)}")

    anchors = _parse_anchor_refs(book_dir)
    anchor_payload = [
        {
            "anchor_id": anchor.anchor_id,
            "name": anchor.name,
            "image_ref": anchor.image_ref,
        }
        for anchor in anchors
    ]

    canon_context = {
        "book_rel_path": _library_rel_path(book_dir),
        "stories": canon_stories,
        "reference_pdf": {
            "exists": reference_pdf.exists(),
            "path": _library_rel_path(reference_pdf),
            "sha256": _sha256_text(pdf_text) if pdf_text else "",
            "text_excerpt": _truncate_text(pdf_text, 16000),
            "text_chars": len(pdf_text),
        },
        "anchors": anchor_payload,
    }
    return canon_context, warnings


def _contains_normalized_phrase(haystack: str, phrase: str) -> bool:
    if not haystack or not phrase:
        return False
    pattern = re.compile(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])")
    return bool(pattern.search(haystack))


def _detect_prohibited_term_findings(
    pages: list[NotebookPage],
    glossary_terms: list[GlossaryTerm],
) -> list[dict[str, str]]:
    page_texts = {
        page.page_number: _normalize_for_match(f"{page.text}\n{page.image_prompt}")
        for page in pages
    }

    detections: dict[tuple[str, str, str], set[int]] = {}
    for term in glossary_terms:
        canonical = term.canonical or term.term
        for prohibited_variant in term.prohibited:
            normalized_variant = _normalize_for_match(prohibited_variant)
            if len(normalized_variant) < 2:
                continue

            for page_number, normalized_content in page_texts.items():
                if _contains_normalized_phrase(normalized_content, normalized_variant):
                    key = (term.term, canonical, prohibited_variant)
                    detections.setdefault(key, set()).add(page_number)

    findings: list[dict[str, str]] = []
    for index, key in enumerate(sorted(detections.keys()), start=1):
        term_name, canonical, prohibited_variant = key
        pages_found = sorted(detections[key])
        pages_label = ", ".join(f"{number:02d}" for number in pages_found)
        suggested = f"Reemplazar '{prohibited_variant}' por '{canonical}'."
        term = next((item for item in glossary_terms if item.term == term_name), None)
        if term and term.allowed:
            suggested = (
                f"Reemplazar '{prohibited_variant}' por '{canonical}'. "
                f"Variantes permitidas: {', '.join(term.allowed)}."
            )

        findings.append(
            {
                "id": f"TERM-{index:03d}",
                "severity": "critical",
                "category": "terminology",
                "scope": f"paginas {pages_label}",
                "issue": (
                    f"Se detecto variante prohibida '{prohibited_variant}' para el termino '{term_name}'."
                ),
                "evidence": (
                    f"Aparece en paginas {pages_label} segun glosario jerarquico ({term.source_meta_file})."
                    if term
                    else f"Aparece en paginas {pages_label}."
                ),
                "suggested_fix": suggested,
                "state": "open",
            }
        )

    return findings


def _compute_review_metrics(findings: list[dict[str, Any]]) -> dict[str, int]:
    metrics = {
        "critical_open": 0,
        "major_open": 0,
        "minor_open": 0,
        "info_open": 0,
    }

    for finding in findings:
        if str(finding.get("state", "")).strip().lower() != "open":
            continue
        severity = str(finding.get("severity", "")).strip().lower()
        key = f"{severity}_open"
        if key in metrics:
            metrics[key] += 1

    return metrics


def _build_review_ai_markdown(
    *,
    title: str,
    story_id: str,
    book_rel_path: str,
    auto_findings: list[dict[str, str]],
) -> str:
    lines = [
        "# Revision IA asistida",
        "",
        f"- cuento: {story_id}",
        f"- libro: {book_rel_path}",
        f"- titulo: {title}",
        f"- modo: {AI_REVIEW_MODE}",
        "- estado inicial: pending",
        "",
        "## Reglas de criticidad",
        "- critical: contradiccion de canon o terminologia prohibida.",
        "- major: inconsistencia texto/prompt o desvio semantico relevante.",
        "- minor/info: tono infantil, claridad, repeticion y estilo.",
        "",
        "## Hallazgos automaticos (terminologia prohibida)",
    ]

    if not auto_findings:
        lines.append("- sin hallazgos automaticos")
    else:
        for finding in auto_findings:
            lines.append(
                f"- [{finding['severity']}] {finding['scope']}: {finding['issue']}"
            )

    lines.extend(
        [
            "",
            "## Pasos de revision manual con Codex",
            "1. Revisar `ai_context.json` para contraste con canon, PDF y glosario.",
            "2. Completar o ajustar `review_ai.json` (status, summary, findings, metrics).",
            "3. Ejecutar `python manage.py inbox-review-validate --batch-id <id>`.",
            "4. Aplicar con `inbox-apply --approve` solo cuando no haya bloqueo.",
            "",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def _build_ai_context(
    *,
    story_id: str,
    title: str,
    book_rel_path: str,
    input_rel_path: str,
    proposal_rel_path: str,
    pages: list[NotebookPage],
    glossary_terms: list[GlossaryTerm],
    glossary_sources: list[dict[str, Any]],
    canon_context: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "review_mode": AI_REVIEW_MODE,
        "generated_at": _utc_now().isoformat(),
        "story": {
            "story_id": story_id,
            "title": title,
            "book_rel_path": book_rel_path,
            "input_file": input_rel_path,
            "proposal_file": proposal_rel_path,
            "pages_detected": len(pages),
            "pages": [
                {
                    "page_number": page.page_number,
                    "text": page.text,
                    "image_prompt": page.image_prompt,
                }
                for page in pages
            ],
        },
        "canon_context": canon_context,
        "glossary": {
            "merge_policy": "root_to_leaf_override",
            "sources": glossary_sources,
            "terms": [
                {
                    "termino": term.term,
                    "canonico": term.canonical,
                    "permitidas": term.allowed,
                    "prohibidas": term.prohibited,
                    "notas": term.notes,
                    "source_meta_file": term.source_meta_file,
                    "source_node": term.source_node,
                }
                for term in glossary_terms
            ],
        },
        "criticality_rules": {
            "critical": "Contradiccion de canon o uso de termino prohibido.",
            "major": "Inconsistencia entre texto/prompt o desvio semantico relevante.",
            "minor_info": "Estilo, tono infantil, claridad o repeticion.",
        },
        "workflow_notes": [
            "Este contexto se revisa manualmente con Codex en chat.",
            "No hay llamadas automaticas a API externa para la auditoria semantica.",
            "El gate de inbox-apply depende de review_ai.json.",
        ],
        "warnings": warnings,
    }


def _validate_review_ai_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("review_ai.json debe ser un objeto JSON.")

    errors: list[str] = []

    status = payload.get("status")
    if not isinstance(status, str) or status not in AI_REVIEW_STATUSES:
        errors.append("'status' debe ser uno de: pending|approved|blocked|approved_with_warnings.")

    review_mode = payload.get("review_mode")
    if review_mode != AI_REVIEW_MODE:
        errors.append(f"'review_mode' debe ser '{AI_REVIEW_MODE}'.")

    summary = payload.get("summary")
    if not isinstance(summary, str):
        errors.append("'summary' debe ser string.")

    findings = payload.get("findings")
    if not isinstance(findings, list):
        errors.append("'findings' debe ser lista.")
        findings = []

    required_finding_fields = [
        "id",
        "severity",
        "category",
        "scope",
        "issue",
        "evidence",
        "suggested_fix",
        "state",
    ]

    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            errors.append(f"finding #{index} debe ser objeto.")
            continue

        for field in required_finding_fields:
            value = finding.get(field)
            if not isinstance(value, str):
                errors.append(f"finding #{index}: campo '{field}' debe ser string.")

        finding_id = str(finding.get("id", "")).strip()
        if not finding_id:
            errors.append(f"finding #{index}: 'id' no puede estar vacio.")

        severity = str(finding.get("severity", "")).strip()
        if severity not in AI_FINDING_SEVERITIES:
            errors.append(
                f"finding #{index}: 'severity' debe ser uno de {sorted(AI_FINDING_SEVERITIES)}."
            )

        category = str(finding.get("category", "")).strip()
        if category not in AI_FINDING_CATEGORIES:
            errors.append(
                f"finding #{index}: 'category' debe ser uno de {sorted(AI_FINDING_CATEGORIES)}."
            )

        state = str(finding.get("state", "")).strip()
        if state not in AI_FINDING_STATES:
            errors.append(
                f"finding #{index}: 'state' debe ser uno de {sorted(AI_FINDING_STATES)}."
            )

    metrics = payload.get("metrics")
    metric_keys = ["critical_open", "major_open", "minor_open", "info_open"]
    if not isinstance(metrics, dict):
        errors.append("'metrics' debe ser objeto.")
        metrics = {}

    for key in metric_keys:
        value = metrics.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"metrics['{key}'] debe ser entero >= 0.")

    computed_metrics = _compute_review_metrics(findings)
    for key in metric_keys:
        provided = metrics.get(key)
        if isinstance(provided, int) and provided != computed_metrics[key]:
            errors.append(
                f"metrics['{key}'] inconsistente. Esperado={computed_metrics[key]}, actual={provided}."
            )

    if status == "approved" and sum(computed_metrics.values()) > 0:
        errors.append("status=approved requiere cero findings abiertos.")

    if errors:
        formatted = "\n".join(f"- {item}" for item in errors)
        raise ValueError(f"review_ai.json invalido:\n{formatted}")

    blocking_reasons: list[str] = []
    if status in {"pending", "blocked"}:
        blocking_reasons.append(f"status={status}")
    if computed_metrics["critical_open"] > 0:
        blocking_reasons.append("critical_open > 0")

    return {
        "status": status,
        "metrics": computed_metrics,
        "blocking": bool(blocking_reasons),
        "blocking_reasons": blocking_reasons,
        "findings_count": len(findings),
    }


def _validate_review_ai_file(batch_dir: Path) -> dict[str, Any]:
    review_file = batch_dir / "review_ai.json"
    if not review_file.exists() or not review_file.is_file():
        raise FileNotFoundError(f"No existe review_ai.json en el batch: {_library_rel_path(batch_dir)}")

    raw_text = review_file.read_text(encoding="utf-8-sig", errors="replace")
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"review_ai.json no es JSON valido: {exc}") from exc

    validated = _validate_review_ai_payload(payload)
    validated["review_file"] = _library_rel_path(review_file)
    return validated


def inbox_review_validate(*, batch_id: str) -> dict[str, Any]:
    normalized_batch_id = batch_id.strip()
    if not normalized_batch_id:
        raise ValueError("batch_id no puede estar vacio.")

    batch_dir = LIBRARY_ROOT / "_inbox" / normalized_batch_id
    if not batch_dir.exists() or not batch_dir.is_dir():
        raise FileNotFoundError(f"No existe el batch: {normalized_batch_id}")

    validated = _validate_review_ai_file(batch_dir)
    metrics = validated["metrics"]
    return {
        "batch_id": normalized_batch_id,
        "review_file": validated["review_file"],
        "status": validated["status"],
        "findings": validated["findings_count"],
        "critical_open": metrics["critical_open"],
        "major_open": metrics["major_open"],
        "minor_open": metrics["minor_open"],
        "info_open": metrics["info_open"],
        "blocking": validated["blocking"],
        "warnings": validated["blocking_reasons"],
    }


def inbox_parse(*, input_path: str, book_rel_path: str, story_id: str) -> dict[str, Any]:
    normalized_story_id = story_id.strip()
    if not re.fullmatch(r"\d{2}", normalized_story_id):
        raise ValueError("story_id debe tener formato de 2 digitos (NN).")

    normalized_book_rel = book_rel_path.strip().replace("\\", "/").strip("/")
    if not normalized_book_rel:
        raise ValueError("book_rel_path no puede estar vacio.")

    source_file = Path(input_path).resolve()
    if not source_file.exists() or not source_file.is_file():
        raise FileNotFoundError(f"No existe el archivo de entrada: {source_file}")

    raw_input = source_file.read_text(encoding="utf-8", errors="replace")
    repaired_input = _repair_mojibake(raw_input)

    title, portada_prompt, pages, warnings = _parse_notebook_markdown(repaired_input)

    book_dir = (LIBRARY_ROOT / normalized_book_rel).resolve()
    anchors = _parse_anchor_refs(book_dir) if book_dir.exists() else []
    page_requirements = {page.page_number: _detect_requirements(page, anchors) for page in pages}

    glossary_terms, glossary_sources, glossary_warnings = _load_hierarchical_glossary(normalized_book_rel)
    warnings.extend(glossary_warnings)

    canon_context, canon_warnings = _collect_canon_context(book_dir=book_dir, story_id=normalized_story_id)
    warnings.extend(canon_warnings)

    auto_findings = _detect_prohibited_term_findings(pages, glossary_terms)

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
    ai_context_file = batch_dir / "ai_context.json"
    review_ai_md_file = batch_dir / "review_ai.md"
    review_ai_json_file = batch_dir / "review_ai.json"
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

    ai_context_payload = _build_ai_context(
        story_id=normalized_story_id,
        title=title,
        book_rel_path=normalized_book_rel,
        input_rel_path=_library_rel_path(input_copy),
        proposal_rel_path=_library_rel_path(proposal_file),
        pages=pages,
        glossary_terms=glossary_terms,
        glossary_sources=glossary_sources,
        canon_context=canon_context,
        warnings=warnings,
    )
    ai_context_file.write_text(json.dumps(ai_context_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    review_ai_payload = {
        "status": "pending",
        "review_mode": AI_REVIEW_MODE,
        "summary": "Completar tras revision semantica manual con Codex.",
        "findings": auto_findings,
        "metrics": _compute_review_metrics(auto_findings),
        "generated_at": _utc_now().isoformat(),
    }
    review_ai_json_file.write_text(
        json.dumps(review_ai_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    review_ai_md_file.write_text(
        _build_review_ai_markdown(
            title=title,
            story_id=normalized_story_id,
            book_rel_path=normalized_book_rel,
            auto_findings=auto_findings,
        ),
        encoding="utf-8",
    )

    manifest = {
        "batch_id": batch_id,
        "status": "proposed",
        "story_id": normalized_story_id,
        "book_rel_path": normalized_book_rel,
        "input_source": str(source_file),
        "input_file": _library_rel_path(input_copy),
        "normalized_file": _library_rel_path(normalized_copy),
        "proposal_file": _library_rel_path(proposal_file),
        "review_file": _library_rel_path(review_file),
        "ai_context_file": _library_rel_path(ai_context_file),
        "review_ai_markdown": _library_rel_path(review_ai_md_file),
        "review_ai_file": _library_rel_path(review_ai_json_file),
        "created_at": _utc_now().isoformat(),
        "warnings": warnings,
        "hashes": {
            "input_sha256": _sha256_text(raw_input),
            "normalized_sha256": _sha256_text(repaired_input),
            "proposal_sha256": _sha256_text(proposal_markdown),
            "ai_context_sha256": _sha256_text(json.dumps(ai_context_payload, ensure_ascii=False)),
            "review_ai_sha256": _sha256_text(json.dumps(review_ai_payload, ensure_ascii=False)),
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
        "manifest": _library_rel_path(manifest_file),
        "proposal": _library_rel_path(proposal_file),
        "ai_context": _library_rel_path(ai_context_file),
        "review_ai": _library_rel_path(review_ai_json_file),
    }


def inbox_apply(
    *,
    batch_id: str,
    approve: bool,
    force: bool = False,
    force_reason: str | None = None,
) -> dict[str, Any]:
    if not approve:
        raise ValueError("Debes usar --approve para aplicar una propuesta.")

    normalized_batch_id = batch_id.strip()
    if not normalized_batch_id:
        raise ValueError("batch_id no puede estar vacio.")

    normalized_force_reason = (force_reason or "").strip()
    if force and not normalized_force_reason:
        raise ValueError("Debes indicar --force-reason cuando uses --force.")

    batch_dir = LIBRARY_ROOT / "_inbox" / normalized_batch_id
    manifest_file = batch_dir / "manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(f"No existe manifest para el batch: {normalized_batch_id}")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8-sig", errors="replace"))
    status = str(manifest.get("status", ""))
    if status != "proposed" and not force:
        raise ValueError(f"El batch {normalized_batch_id} no esta en estado proposed (actual: {status}).")

    review_gate: dict[str, Any] | None = None
    review_gate_error = ""

    if force:
        try:
            review_gate = _validate_review_ai_file(batch_dir)
        except Exception as exc:
            review_gate_error = str(exc)
    else:
        review_gate = _validate_review_ai_file(batch_dir)
        if review_gate["blocking"]:
            reasons = "; ".join(review_gate["blocking_reasons"])
            raise ValueError(f"Gate IA bloqueado para batch {normalized_batch_id}: {reasons}")

    story_id = str(manifest.get("story_id", "")).strip()
    book_rel_path = str(manifest.get("book_rel_path", "")).strip().replace("\\", "/").strip("/")
    proposal_rel = str(manifest.get("proposal_file", "")).strip().replace("\\", "/")
    if not re.fullmatch(r"\d{2}", story_id):
        raise ValueError("manifest invalido: story_id debe tener formato NN.")
    if not book_rel_path or not proposal_rel:
        raise ValueError("manifest invalido: faltan book_rel_path/proposal_file.")

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
    manifest["applied_target"] = _library_rel_path(target_file)
    manifest["forced_apply"] = bool(force)
    manifest["ai_review_gate"] = {
        "checked_at": _utc_now().isoformat(),
        "status": review_gate.get("status") if isinstance(review_gate, dict) else "unknown",
        "blocking": review_gate.get("blocking") if isinstance(review_gate, dict) else None,
        "metrics": review_gate.get("metrics") if isinstance(review_gate, dict) else {},
    }

    if force:
        manifest["force_reason"] = normalized_force_reason
        manifest["forced_at"] = _utc_now().isoformat()
        if review_gate_error:
            manifest["forced_gate_error"] = review_gate_error
    else:
        manifest.pop("force_reason", None)
        manifest.pop("forced_at", None)
        manifest.pop("forced_gate_error", None)

    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    apply_warnings: list[str] = []
    if review_gate_error:
        apply_warnings.append(review_gate_error)

    return {
        "batch_id": normalized_batch_id,
        "story_id": story_id,
        "book_rel_path": book_rel_path,
        "target": _library_rel_path(target_file),
        "backup_created": backed_up,
        "forced_apply": bool(force),
        "warnings": apply_warnings,
    }
