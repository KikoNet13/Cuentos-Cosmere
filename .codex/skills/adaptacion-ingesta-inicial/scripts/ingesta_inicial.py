#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STORY_FILE_RE = re.compile(r"^(\d{2})\.md$", re.IGNORECASE)
PAGE_HEADING_RE = re.compile(r"(?im)^##\s*P[aá]gina\s+(\d{1,3})\s*$")
SEVERITIES = ("critical", "major", "minor", "info")
CONTEXT_SCHEMA_VERSION = "1.0"
ISSUES_SCHEMA_VERSION = "1.0"
STORY_SCHEMA_VERSION = "1.1"


@dataclass
class StorySource:
    story_id: str
    md_path: Path
    pdf_path: Path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def normalize_book_rel(raw_value: str) -> str:
    return raw_value.strip().replace("\\", "/").strip("/")


def slugify(raw_value: str) -> str:
    value = unicodedata.normalize("NFKD", raw_value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "book"


def project_root_from_script(script_path: Path) -> Path:
    current = script_path.resolve()
    for parent in current.parents:
        if (parent / "manage.py").exists():
            return parent
    return script_path.resolve().parents[4]


def load_json_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} debe contener un objeto JSON.")
    return payload


def write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_issue(
    *,
    story_id: str,
    index: int,
    severity: str,
    category: str,
    page_number: int | None,
    evidence: str,
    suggested_action: str,
    status: str = "open",
) -> dict[str, Any]:
    return {
        "issue_id": f"{story_id}-I{index:03d}",
        "severity": severity,
        "category": category,
        "page_number": page_number,
        "evidence": evidence.strip(),
        "suggested_action": suggested_action.strip(),
        "status": status,
    }


def issue_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = {key: 0 for key in SEVERITIES}
    for issue in issues:
        severity = str(issue.get("severity", "")).strip().lower()
        if severity in counts:
            counts[severity] += 1
    return counts


def discover_story_sources(inbox_book_dir: Path) -> tuple[list[StorySource], list[str]]:
    grouped: dict[str, list[Path]] = {}
    for md_path in sorted(inbox_book_dir.rglob("*.md")):
        if "_ignore" in md_path.parts:
            continue
        match = STORY_FILE_RE.fullmatch(md_path.name)
        if not match:
            continue
        story_id = match.group(1)
        grouped.setdefault(story_id, []).append(md_path)

    errors: list[str] = []
    sources: list[StorySource] = []
    for story_id in sorted(grouped):
        md_paths = grouped[story_id]
        if len(md_paths) > 1:
            formatted = ", ".join(path.as_posix() for path in md_paths)
            errors.append(f"story_id duplicado {story_id}: {formatted}")
            continue
        md_path = md_paths[0]
        sources.append(
            StorySource(
                story_id=story_id,
                md_path=md_path,
                pdf_path=md_path.with_suffix(".pdf"),
            )
        )
    return sources, errors


def extract_labeled_codeblock(section_text: str, label: str) -> str:
    pattern = re.compile(rf"(?is)^{label}\s*:\s*```(?:text)?\s*(.*?)\s*```", re.MULTILINE)
    match = pattern.search(section_text)
    if not match:
        return ""
    return match.group(1).strip()


def parse_story_markdown(md_path: Path) -> tuple[dict[str, Any], list[tuple[str, str, int | None]]]:
    content = md_path.read_text(encoding="utf-8")
    issues: list[tuple[str, str, int | None]] = []

    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", content)
    title = title_match.group(1).strip() if title_match else f"Cuento {md_path.stem}"
    if not title_match:
        issues.append(("major", "markdown.missing_title", None))

    cover_prompt = extract_labeled_codeblock(content, "Portada")
    if not cover_prompt:
        issues.append(("minor", "markdown.missing_cover", None))

    headings = list(PAGE_HEADING_RE.finditer(content))
    pages: list[dict[str, Any]] = []
    if not headings:
        issues.append(("critical", "markdown.no_pages", None))
        return {"title": title, "cover_prompt": cover_prompt, "pages": pages}, issues

    for index, heading in enumerate(headings):
        start = heading.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
        section = content[start:end]
        page_number = int(heading.group(1))
        text_original = extract_labeled_codeblock(section, "Texto")
        prompt_original = extract_labeled_codeblock(section, "Imagen")

        if not text_original:
            issues.append(("major", "markdown.missing_text_block", page_number))
        if not prompt_original:
            issues.append(("major", "markdown.missing_image_block", page_number))

        pages.append(
            {
                "page_number": page_number,
                "text_original": text_original,
                "prompt_original": prompt_original,
            }
        )

    ordered_numbers = sorted(item["page_number"] for item in pages)
    if ordered_numbers and ordered_numbers[0] != 1:
        issues.append(("major", "markdown.page_sequence_starts_not_1", None))

    if ordered_numbers:
        expected = set(range(ordered_numbers[0], ordered_numbers[-1] + 1))
        missing = sorted(expected.difference(set(ordered_numbers)))
        for value in missing:
            issues.append(("major", "markdown.missing_page_number", value))

    return {"title": title, "cover_prompt": cover_prompt, "pages": pages}, issues


def extract_pdf_pages_text(pdf_path: Path) -> tuple[list[str] | None, str | None]:
    reader_cls = None
    try:
        from pypdf import PdfReader as _PdfReader  # type: ignore

        reader_cls = _PdfReader
    except Exception:
        try:
            from PyPDF2 import PdfReader as _PdfReader  # type: ignore

            reader_cls = _PdfReader
        except Exception:
            return None, "No hay parser PDF disponible (pypdf/PyPDF2)."

    try:
        reader = reader_cls(str(pdf_path))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        return pages, None
    except Exception as exc:
        return None, f"No se pudo extraer texto de PDF: {exc}"


def tokenize_words(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9áéíóúñÁÉÍÓÚÑ]{3,}", text.lower())
    return set(words)


def detect_pdf_mismatch_issues(
    *,
    story_id: str,
    parsed_story: dict[str, Any],
    pdf_path: Path,
    start_index: int,
) -> tuple[list[dict[str, Any]], int]:
    issues: list[dict[str, Any]] = []
    next_index = start_index

    if not pdf_path.exists():
        issues.append(
            build_issue(
                story_id=story_id,
                index=next_index,
                severity="critical",
                category="input.missing_pdf",
                page_number=None,
                evidence=f"No existe PDF de referencia para {pdf_path.name}.",
                suggested_action="Agregar NN.pdf con el mismo identificador antes de cierre editorial.",
            )
        )
        return issues, next_index + 1

    pages_text, error = extract_pdf_pages_text(pdf_path)
    if error:
        issues.append(
            build_issue(
                story_id=story_id,
                index=next_index,
                severity="major",
                category="pdf.unreadable",
                page_number=None,
                evidence=error,
                suggested_action="Revisar el PDF y confirmar extractibilidad de texto.",
            )
        )
        return issues, next_index + 1

    if pages_text is None:
        return issues, next_index

    pages = list(parsed_story.get("pages", []))
    if len(pages) != len(pages_text):
        issues.append(
            build_issue(
                story_id=story_id,
                index=next_index,
                severity="major",
                category="pdf.page_count_mismatch",
                page_number=None,
                evidence=f"Markdown={len(pages)} paginas, PDF={len(pages_text)} paginas.",
                suggested_action="Revisar pairing NN.md/NN.pdf y consistencia por pagina.",
            )
        )
        next_index += 1

    for page in pages:
        page_number = int(page.get("page_number", 0))
        md_tokens = tokenize_words(str(page.get("text_original", "")))
        pdf_text = pages_text[page_number - 1] if 0 < page_number <= len(pages_text) else ""
        pdf_tokens = tokenize_words(pdf_text)

        if not pdf_text.strip():
            issues.append(
                build_issue(
                    story_id=story_id,
                    index=next_index,
                    severity="major",
                    category="pdf.page_without_text",
                    page_number=page_number,
                    evidence="No se extrajo texto util en la pagina PDF asociada.",
                    suggested_action="Confirmar si la pagina es imagen o si se requiere OCR externo.",
                )
            )
            next_index += 1
            continue

        if not md_tokens or not pdf_tokens:
            continue

        overlap = len(md_tokens.intersection(pdf_tokens)) / max(len(md_tokens), 1)
        if overlap < 0.08:
            issues.append(
                build_issue(
                    story_id=story_id,
                    index=next_index,
                    severity="critical",
                    category="pdf.low_lexical_overlap",
                    page_number=page_number,
                    evidence=f"Solapamiento lexico bajo ({overlap:.2f}).",
                    suggested_action="Validar que la propuesta mantiene el contenido canonico base.",
                )
            )
            next_index += 1

    return issues, next_index


def collect_ambiguous_terms(stories: list[dict[str, Any]]) -> list[str]:
    quoted_terms: set[str] = set()
    name_counter: Counter[str] = Counter()

    common = {
        "Pagina",
        "Texto",
        "Imagen",
        "Portada",
        "Una",
        "Uno",
        "El",
        "La",
        "Los",
        "Las",
        "Y",
        "De",
        "Del",
        "En",
        "Con",
        "Al",
        "Por",
        "Que",
        "Pero",
        "Un",
        "Una",
    }

    quote_patterns = [
        re.compile(r'"([^"\n]{2,60})"'),
        re.compile(r"«([^»\n]{2,60})»"),
    ]
    name_pattern = re.compile(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,})?\b")

    for story in stories:
        chunks: list[str] = [str(story.get("title", "")), str(story.get("cover_prompt", ""))]
        for page in story.get("pages", []):
            chunks.append(str(page.get("text_original", "")))
            chunks.append(str(page.get("prompt_original", "")))
        joined = "\n".join(chunks)

        for pattern in quote_patterns:
            for match in pattern.findall(joined):
                term = " ".join(match.split()).strip()
                if term:
                    quoted_terms.add(term)

        for match in name_pattern.findall(joined):
            candidate = " ".join(match.split()).strip()
            if not candidate or candidate in common:
                continue
            name_counter[candidate] += 1

    names = {term for term, qty in name_counter.items() if qty >= 2}
    all_terms = sorted(quoted_terms.union(names), key=lambda item: item.casefold())
    return all_terms


def parse_answers(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = load_json_file(path)
    answers = payload.get("answers", payload)
    if not isinstance(answers, dict):
        return {}
    result: dict[str, Any] = dict(answers)
    if isinstance(payload.get("book_rel_path"), str) and "book_rel_path" not in result:
        result["book_rel_path"] = payload["book_rel_path"]
    if payload.get("target_age") is not None and "target_age" not in result:
        result["target_age"] = payload["target_age"]
    if isinstance(payload.get("glossary"), dict) and "glossary" not in result:
        result["glossary"] = payload["glossary"]
    return result


def validate_target_age(raw_value: Any) -> int | None:
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None
    if value < 3 or value > 18:
        return None
    return value


def glossary_answer_for(term: str, glossary_answers: dict[str, Any]) -> str:
    raw_value = glossary_answers.get(term)
    if raw_value is None:
        raw_value = glossary_answers.get(slugify(term))
    value = str(raw_value or "").strip()
    return value


def build_story_json_payload(
    *,
    source: StorySource,
    parsed_story: dict[str, Any],
    book_rel_path: str,
    target_age: int,
    root_dir: Path,
) -> dict[str, Any]:
    now = utc_now_iso()
    title = str(parsed_story.get("title", "")).strip() or f"Cuento {source.story_id}"
    cover_prompt = str(parsed_story.get("cover_prompt", "")).strip()
    pages_payload: list[dict[str, Any]] = []
    for page in sorted(parsed_story.get("pages", []), key=lambda item: int(item.get("page_number", 0))):
        text_original = str(page.get("text_original", "")).strip()
        prompt_original = str(page.get("prompt_original", "")).strip()
        pages_payload.append(
            {
                "page_number": int(page.get("page_number", 0)),
                "status": "draft",
                "text": {"original": text_original, "current": text_original},
                "images": {
                    "main": {
                        "slot_name": "main",
                        "status": "draft",
                        "prompt": {"original": prompt_original, "current": prompt_original},
                        "active_id": "",
                        "alternatives": [],
                    }
                },
            }
        )

    proposal_rel = normalize_rel(source.md_path, root_dir)
    pdf_rel = normalize_rel(source.pdf_path, root_dir) if source.pdf_path.exists() else ""

    return {
        "schema_version": STORY_SCHEMA_VERSION,
        "story_id": source.story_id,
        "title": title,
        "story_title": title,
        "status": "in_review",
        "book_rel_path": book_rel_path,
        "created_at": now,
        "updated_at": now,
        "cover": {
            "status": "draft",
            "prompt": {"original": cover_prompt, "current": cover_prompt},
            "asset_rel_path": "",
            "notes": "",
        },
        "source_refs": {
            "proposal_md_rel_path": proposal_rel,
            "reference_pdf_rel_path": pdf_rel,
            "inbox_book_title": source.md_path.parent.name,
        },
        "ingest_meta": {
            "phase": "initial_ingest",
            "target_age": target_age,
            "generated_at": now,
            "generated_by": "adaptacion-ingesta-inicial",
            "semantic_mode": "codex_chat",
        },
        "pages": pages_payload,
    }


def merge_context_payload(
    *,
    existing: dict[str, Any] | None,
    book_rel_path: str,
    book_title: str,
    target_age: int,
    story_rel_paths: list[str],
    glossary_terms: list[str],
    glossary_answers: dict[str, Any],
) -> dict[str, Any]:
    base = existing if isinstance(existing, dict) else {}
    glossary_map: dict[str, dict[str, Any]] = {}
    for entry in base.get("glossary", []):
        if not isinstance(entry, dict):
            continue
        term = str(entry.get("term", "")).strip()
        if not term:
            continue
        glossary_map[term] = dict(entry)

    for term in glossary_terms:
        confirmed_value = glossary_answer_for(term, glossary_answers)
        status = "confirmed" if confirmed_value else "pending"
        canonical = confirmed_value
        previous = glossary_map.get(term, {})
        if not canonical and previous.get("status") == "confirmed":
            canonical = str(previous.get("canonical", "")).strip()
            status = "confirmed" if canonical else "pending"
        glossary_map[term] = {
            "term": term,
            "status": status,
            "canonical": canonical,
        }

    all_story_rel = {
        str(item).strip()
        for item in list(base.get("stories", [])) + list(story_rel_paths)
        if str(item).strip()
    }
    glossary_items = sorted(glossary_map.values(), key=lambda item: str(item.get("term", "")).casefold())
    ambiguities = [
        {"term": item["term"], "status": item["status"]}
        for item in glossary_items
        if item["status"] != "confirmed"
    ]

    notes = [
        f"Ingesta inicial actualizada {utc_now_iso()}",
        "Analisis semantico esperado por skill conversacional Codex.",
    ]

    return {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "book_rel_path": book_rel_path,
        "book_title": book_title,
        "target_age": target_age,
        "updated_at": utc_now_iso(),
        "stories": sorted(all_story_rel),
        "glossary": glossary_items,
        "ambiguities": ambiguities,
        "notes": notes,
    }


def run_ingesta(
    *,
    root_dir: Path,
    inbox_book_title: str,
    book_rel_path_arg: str | None,
    answers: dict[str, Any],
    dry_run: bool,
) -> dict[str, Any]:
    inbox_dir = root_dir / "library" / "_inbox" / inbox_book_title
    if not inbox_dir.exists() or not inbox_dir.is_dir():
        return {
            "phase": "failed",
            "pending_questions": [],
            "planned_outputs": [],
            "written_outputs": [],
            "metrics": {},
            "errors": [f"No existe inbox: {inbox_dir.as_posix()}"],
        }

    sources, discovery_errors = discover_story_sources(inbox_dir)
    if discovery_errors:
        return {
            "phase": "failed",
            "pending_questions": [],
            "planned_outputs": [],
            "written_outputs": [],
            "metrics": {},
            "errors": discovery_errors,
        }
    if not sources:
        return {
            "phase": "failed",
            "pending_questions": [],
            "planned_outputs": [],
            "written_outputs": [],
            "metrics": {},
            "errors": ["No se encontraron archivos NN.md procesables."],
        }

    proposed_book_rel = normalize_book_rel(book_rel_path_arg or str(answers.get("book_rel_path", "")).strip())
    if not proposed_book_rel:
        proposed_book_rel = f"cosmere/{slugify(inbox_book_title)}"

    parsed_stories: dict[str, dict[str, Any]] = {}
    issues_by_story: dict[str, list[dict[str, Any]]] = {}
    pages_total = 0
    all_ambiguity_inputs: list[dict[str, Any]] = []
    for source in sources:
        parsed_story, parse_issues = parse_story_markdown(source.md_path)
        parsed_stories[source.story_id] = parsed_story
        pages_total += len(parsed_story.get("pages", []))
        story_issues: list[dict[str, Any]] = []
        issue_index = 1
        for severity, category, page_number in parse_issues:
            evidence = f"Hallazgo estructural en {source.md_path.name}."
            suggested = "Corregir estructura de markdown antes de cierre editorial."
            story_issues.append(
                build_issue(
                    story_id=source.story_id,
                    index=issue_index,
                    severity=severity,
                    category=category,
                    page_number=page_number,
                    evidence=evidence,
                    suggested_action=suggested,
                )
            )
            issue_index += 1

        pdf_issues, next_index = detect_pdf_mismatch_issues(
            story_id=source.story_id,
            parsed_story=parsed_story,
            pdf_path=source.pdf_path,
            start_index=issue_index,
        )
        story_issues.extend(pdf_issues)
        issue_index = next_index
        issues_by_story[source.story_id] = story_issues
        all_ambiguity_inputs.append(parsed_story)

    glossary_terms = collect_ambiguous_terms(all_ambiguity_inputs)
    glossary_answers_raw = answers.get("glossary", {})
    glossary_answers = glossary_answers_raw if isinstance(glossary_answers_raw, dict) else {}

    pending_questions: list[dict[str, Any]] = []
    if not normalize_book_rel(book_rel_path_arg or str(answers.get("book_rel_path", ""))):
        pending_questions.append(
            {
                "id": "book_rel_path",
                "kind": "text",
                "prompt": "Confirma book_rel_path destino para la ingesta inicial.",
                "default": proposed_book_rel,
                "required": True,
            }
        )

    target_age = validate_target_age(answers.get("target_age"))
    if target_age is None:
        pending_questions.append(
            {
                "id": "target_age",
                "kind": "number",
                "prompt": "Indica target_age (3-18) para este libro.",
                "required": True,
                "constraints": {"min": 3, "max": 18},
            }
        )

    for term in glossary_terms:
        if glossary_answer_for(term, glossary_answers):
            continue
        pending_questions.append(
            {
                "id": f"glossary::{slugify(term)}",
                "kind": "text",
                "prompt": f"Confirma termino canonico para '{term}'.",
                "term": term,
                "default": term,
                "required": True,
            }
        )

    planned_outputs: list[str] = []
    for source in sources:
        planned_outputs.append(f"library/{proposed_book_rel}/{source.story_id}.json")
        planned_outputs.append(f"library/{proposed_book_rel}/_reviews/{source.story_id}.issues.json")
    planned_outputs.append(f"library/{proposed_book_rel}/_reviews/adaptation_context.json")
    planned_outputs = sorted(set(planned_outputs))

    severity_total = {key: 0 for key in SEVERITIES}
    for items in issues_by_story.values():
        counts = issue_counts(items)
        for key in SEVERITIES:
            severity_total[key] += counts[key]

    metrics = {
        "stories": len(sources),
        "pages": pages_total,
        "issues_total": sum(severity_total.values()),
        "issues_by_severity": severity_total,
        "glossary_terms": len(glossary_terms),
        "pending_questions": len(pending_questions),
    }

    if pending_questions:
        return {
            "phase": "awaiting_user",
            "pending_questions": pending_questions,
            "planned_outputs": planned_outputs,
            "written_outputs": [],
            "metrics": metrics,
            "errors": [],
        }

    assert target_age is not None
    effective_book_rel = normalize_book_rel(book_rel_path_arg or str(answers.get("book_rel_path", "")))
    effective_book_rel = effective_book_rel or proposed_book_rel

    story_rel_paths: list[str] = []
    written_outputs: list[str] = []
    context_existing_path = root_dir / "library" / effective_book_rel / "_reviews" / "adaptation_context.json"
    existing_context: dict[str, Any] | None = None
    if context_existing_path.exists():
        try:
            existing_context = load_json_file(context_existing_path)
        except Exception:
            existing_context = None

    for source in sources:
        parsed_story = parsed_stories[source.story_id]
        story_payload = build_story_json_payload(
            source=source,
            parsed_story=parsed_story,
            book_rel_path=effective_book_rel,
            target_age=target_age,
            root_dir=root_dir,
        )

        story_rel = f"{effective_book_rel}/{source.story_id}"
        story_rel_paths.append(story_rel)
        story_file = root_dir / "library" / effective_book_rel / f"{source.story_id}.json"
        issues_file = root_dir / "library" / effective_book_rel / "_reviews" / f"{source.story_id}.issues.json"

        story_issues = issues_by_story[source.story_id]
        issues_payload = {
            "schema_version": ISSUES_SCHEMA_VERSION,
            "story_id": source.story_id,
            "story_rel_path": story_rel,
            "generated_at": utc_now_iso(),
            "summary": issue_counts(story_issues),
            "issues": story_issues,
        }

        if not dry_run:
            write_json_file(story_file, story_payload)
            write_json_file(issues_file, issues_payload)

        written_outputs.extend(
            [
                f"library/{effective_book_rel}/{source.story_id}.json",
                f"library/{effective_book_rel}/_reviews/{source.story_id}.issues.json",
            ]
        )

    context_payload = merge_context_payload(
        existing=existing_context,
        book_rel_path=effective_book_rel,
        book_title=inbox_book_title,
        target_age=target_age,
        story_rel_paths=story_rel_paths,
        glossary_terms=glossary_terms,
        glossary_answers=glossary_answers,
    )
    if not dry_run:
        write_json_file(context_existing_path, context_payload)
    written_outputs.append(f"library/{effective_book_rel}/_reviews/adaptation_context.json")

    return {
        "phase": "completed",
        "pending_questions": [],
        "planned_outputs": planned_outputs,
        "written_outputs": sorted(set(written_outputs)),
        "metrics": metrics,
        "errors": [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingesta inicial interactiva de propuestas NN.md + NN.pdf a NN.json + sidecars."
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Ejecuta la ingesta inicial.")
    run_parser.add_argument("--inbox-book-title", required=True, help="Nombre de carpeta bajo library/_inbox/.")
    run_parser.add_argument("--book-rel-path", default="", help="Ruta destino bajo library/ (opcional).")
    run_parser.add_argument("--answers-json", default="", help="Archivo JSON con respuestas del usuario.")
    run_parser.add_argument("--dry-run", action="store_true", help="Calcula salida sin escribir archivos.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "run":
        parser.print_help()
        return 1

    root_dir = project_root_from_script(Path(__file__))
    answers_path = Path(args.answers_json) if str(args.answers_json).strip() else None

    try:
        answers = parse_answers(answers_path)
    except Exception as exc:
        payload = {
            "phase": "failed",
            "pending_questions": [],
            "planned_outputs": [],
            "written_outputs": [],
            "metrics": {},
            "errors": [f"No se pudo leer answers_json: {exc}"],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1

    result = run_ingesta(
        root_dir=root_dir,
        inbox_book_title=str(args.inbox_book_title).strip(),
        book_rel_path_arg=str(args.book_rel_path).strip() or None,
        answers=answers,
        dry_run=bool(args.dry_run),
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("phase") in {"completed", "awaiting_user"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
