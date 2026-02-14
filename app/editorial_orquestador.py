from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import LIBRARY_ROOT, ROOT_DIR
from .story_store import (
    StoryStoreError,
    load_story,
    save_story_payload,
    set_story_status,
)

STAGE_TEXT_AUDIT = "text_audit"
STAGE_PROMPT_AUDIT = "prompt_audit"
STAGE_TEXT = "text"
STAGE_PROMPT = "prompt"
REVIEW_SCHEMA_VERSION = "1.0"
PIPELINE_SCHEMA_VERSION = "1.0"
CASCADE_SCHEMA_VERSION = "2.0"
CONTEXT_REVIEW_SCHEMA_VERSION = "1.0"
SEVERITY_ORDER = ("critical", "major", "minor", "info")
BLOCKING_SEVERITIES = {"critical", "major"}
MAX_PASSES_BY_SEVERITY = {
    "critical": 5,
    "major": 4,
    "minor": 3,
    "info": 2,
}
VALID_SEVERITY_BANDS = set(SEVERITY_ORDER)

PROMPT_STRUCTURED_LABELS = (
    "SUJETO",
    "ESCENA",
    "ESTILO",
    "COMPOSICION",
    "ILUMINACION_COLOR",
    "CONTINUIDAD",
    "RESTRICCIONES",
)

OPEN_FINDING_DECISIONS = {"pending", "rejected"}
CONTEXT_REVIEW_DECISIONS = {"accepted", "rejected", "defer", "pending"}
CONTEXT_REVIEW_MODE = "light"
CONTEXT_REVIEW_BLOCKING = False
CONTEXT_REVIEW_REPLACEMENT_POLICY = "preferred_alias_else_canonical"
CONTEXT_REVIEW_PENDING_POLICY = "no_impact"


class EditorialOrquestadorError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _validate_book_rel_path(book_rel_path: str) -> str:
    normalized = _normalize_rel_path(book_rel_path)
    if not normalized:
        raise EditorialOrquestadorError("`book_rel_path` no puede estar vacío.")
    return normalized


def _validate_inbox_book_title(inbox_book_title: str) -> str:
    value = str(inbox_book_title).strip()
    if not value:
        raise EditorialOrquestadorError("`inbox_book_title` no puede estar vacío.")
    return value


def _validate_story_id(story_id: str) -> str:
    value = str(story_id).strip()
    if not re.fullmatch(r"\d{2}", value):
        raise EditorialOrquestadorError("`story_id` debe tener formato `NN` (dos dígitos).")
    return value


def _validate_story_exists(book_rel_path: str, story_id: str) -> tuple[str, str]:
    normalized_book = _validate_book_rel_path(book_rel_path)
    normalized_story = _validate_story_id(story_id)
    story_rel_path = f"{normalized_book}/{normalized_story}"
    story_abs_path = (LIBRARY_ROOT / normalized_book / f"{normalized_story}.json").resolve()
    if not story_abs_path.exists() or not story_abs_path.is_file():
        raise EditorialOrquestadorError(
            f"No existe `story_id={normalized_story}` en `book_rel_path={normalized_book}`."
        )
    return normalized_book, story_rel_path


def _validate_severity_band(severity_band: str) -> str:
    normalized = str(severity_band).strip().lower()
    if normalized not in VALID_SEVERITY_BANDS:
        allowed = ", ".join(SEVERITY_ORDER)
        raise EditorialOrquestadorError(
            f"`severity_band` inválido: '{severity_band}'. Valores permitidos: {allowed}."
        )
    return normalized


def _validate_pass_index(pass_index: int) -> int:
    try:
        normalized = int(pass_index)
    except (TypeError, ValueError) as exc:
        raise EditorialOrquestadorError("`pass_index` debe ser un entero >= 1.") from exc
    if normalized < 1:
        raise EditorialOrquestadorError("`pass_index` debe ser >= 1.")
    return normalized


def _to_project_rel(path_abs: Path) -> str:
    return path_abs.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def _looks_like_story_md(path_obj: Path) -> bool:
    return bool(re.fullmatch(r"\d{2}\.md", path_obj.name, re.IGNORECASE))


def _safe_read_markdown(path_obj: Path) -> str:
    raw = path_obj.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _review_paths(book_rel_path: str, story_id: str) -> dict[str, Path]:
    reviews_dir = (LIBRARY_ROOT / _normalize_rel_path(book_rel_path) / "_reviews").resolve()
    return {
        "reviews_dir": reviews_dir,
        "review_json": reviews_dir / f"{story_id}.review.json",
        "review_md": reviews_dir / f"{story_id}.review.md",
        "decisions_json": reviews_dir / f"{story_id}.decisions.json",
        "findings_json": reviews_dir / f"{story_id}.findings.json",
        "choices_json": reviews_dir / f"{story_id}.choices.json",
        "contrast_json": reviews_dir / f"{story_id}.contrast.json",
        "passes_json": reviews_dir / f"{story_id}.passes.json",
        "pipeline_state_json": reviews_dir / "pipeline_state.json",
        "context_chain_json": reviews_dir / "context_chain.json",
        "glossary_merged_json": reviews_dir / "glossary_merged.json",
        "context_review_json": reviews_dir / "context_review.json",
    }


def _write_json(path_obj: Path, payload: dict[str, Any]) -> None:
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    path_obj.write_text(content, encoding="utf-8")


def _read_json(path_obj: Path) -> dict[str, Any] | None:
    if not path_obj.exists() or not path_obj.is_file():
        return None
    try:
        data = json.loads(path_obj.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _dedupe_case_insensitive(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for raw in values:
        token = str(raw).strip()
        if not token:
            continue
        key = token.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(token)
    return output


def _normalize_context_term_key(term_key: str, term: str) -> str:
    candidate = str(term_key).strip().lower()
    if candidate:
        return candidate
    return str(term).strip().lower()


def _normalize_context_decision(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized in CONTEXT_REVIEW_DECISIONS:
        return normalized
    return "pending"


def _normalize_context_list(value: Any) -> list[str]:
    if isinstance(value, list):
        values = [str(item).strip() for item in value]
        return _dedupe_case_insensitive(values)
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    values = [item.strip() for item in re.split(r"[;,]", text) if item.strip()]
    return _dedupe_case_insensitive(values)


def _normalize_context_review_row(row: Any, now_iso: str) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return None
    term = str(row.get("term", "")).strip()
    term_key = _normalize_context_term_key(str(row.get("term_key", "")), term)
    if not term_key:
        return None
    if not term:
        term = term_key
    return {
        "term_key": term_key,
        "term": term,
        "decision": _normalize_context_decision(str(row.get("decision", "pending"))),
        "preferred_alias": str(row.get("preferred_alias", "")).strip(),
        "allowed_add": _normalize_context_list(row.get("allowed_add", [])),
        "forbidden_add": _normalize_context_list(row.get("forbidden_add", [])),
        "notes": str(row.get("notes", "")).strip(),
        "updated_at": str(row.get("updated_at", "")).strip() or now_iso,
    }


def _merge_context_review_decisions(
    existing_rows: list[dict[str, Any]],
    incoming_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    now_iso = _utc_now_iso()
    merged: dict[str, dict[str, Any]] = {}

    for row in existing_rows:
        normalized = _normalize_context_review_row(row, now_iso)
        if not normalized:
            continue
        merged[normalized["term_key"]] = normalized

    for row in incoming_rows:
        normalized = _normalize_context_review_row(row, now_iso)
        if not normalized:
            continue
        normalized["updated_at"] = now_iso
        merged[normalized["term_key"]] = normalized

    return sorted(merged.values(), key=lambda item: str(item.get("term_key", "")))


def _apply_context_review_to_glossary(
    *,
    glossary_base: list[dict[str, Any]],
    review_decisions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    glossary_map: dict[str, dict[str, Any]] = {}
    for row in glossary_base:
        term = str(row.get("term", "")).strip()
        if not term:
            continue
        term_key = term.lower()
        normalized = dict(row)
        canonical = str(normalized.get("canonical", "")).strip() or term
        normalized["canonical"] = canonical
        normalized["allowed"] = _dedupe_case_insensitive(
            [str(item).strip() for item in normalized.get("allowed", [])]
        )
        normalized["forbidden"] = _dedupe_case_insensitive(
            [str(item).strip() for item in normalized.get("forbidden", [])]
        )
        normalized["replacement_target"] = canonical
        glossary_map[term_key] = normalized

    ignored_missing_term = 0
    for decision in review_decisions:
        term_key = str(decision.get("term_key", "")).strip().lower()
        if not term_key:
            continue
        target = glossary_map.get(term_key)
        if not target:
            ignored_missing_term += 1
            continue
        if str(decision.get("decision", "pending")).strip().lower() != "accepted":
            continue

        preferred_alias = str(decision.get("preferred_alias", "")).strip()
        replacement_target = preferred_alias or str(target.get("canonical", "")).strip() or str(
            target.get("term", "")
        ).strip()
        target["replacement_target"] = replacement_target
        target["allowed"] = _dedupe_case_insensitive(
            [str(item).strip() for item in target.get("allowed", [])]
            + [str(item).strip() for item in decision.get("allowed_add", [])]
        )
        target["forbidden"] = _dedupe_case_insensitive(
            [str(item).strip() for item in target.get("forbidden", [])]
            + [str(item).strip() for item in decision.get("forbidden_add", [])]
        )
        notes = str(decision.get("notes", "")).strip()
        if notes:
            base_notes = str(target.get("notes", "")).strip()
            target["notes"] = notes if not base_notes else f"{base_notes}\n{notes}"

    merged = sorted(glossary_map.values(), key=lambda item: str(item.get("term", "")).lower())
    return merged, ignored_missing_term


def _build_context_review_metrics(
    *,
    review_decisions: list[dict[str, Any]],
    ignored_missing_term: int,
) -> dict[str, int]:
    metrics = {
        "total": len(review_decisions),
        "accepted": 0,
        "rejected": 0,
        "defer": 0,
        "pending": 0,
        "ignored_missing_term": int(ignored_missing_term),
    }
    for row in review_decisions:
        decision = _normalize_context_decision(str(row.get("decision", "pending")))
        metrics[decision] += 1
    return metrics


def _context_review_payload_base(*, book_rel_path: str, inbox_book_title: str, generated_at: str) -> dict[str, Any]:
    now_iso = _utc_now_iso()
    return {
        "schema_version": CONTEXT_REVIEW_SCHEMA_VERSION,
        "generated_at": generated_at,
        "updated_at": now_iso,
        "book_rel_path": book_rel_path,
        "inbox_book_title": inbox_book_title,
        "mode": CONTEXT_REVIEW_MODE,
        "blocking": CONTEXT_REVIEW_BLOCKING,
        "replacement_policy": CONTEXT_REVIEW_REPLACEMENT_POLICY,
        "pending_policy": CONTEXT_REVIEW_PENDING_POLICY,
        "decisions": [],
        "metrics": {
            "total": 0,
            "accepted": 0,
            "rejected": 0,
            "defer": 0,
            "pending": 0,
            "ignored_missing_term": 0,
        },
    }


def _read_context_review_payload(*, book_rel_path: str, inbox_book_title: str) -> dict[str, Any]:
    normalized_book = _validate_book_rel_path(book_rel_path)
    inbox_title = _validate_inbox_book_title(inbox_book_title)
    paths = _review_paths(normalized_book, "00")
    existing = _read_json(paths["context_review_json"]) or {}
    generated_at = str(existing.get("generated_at", "")).strip() or _utc_now_iso()
    payload = _context_review_payload_base(
        book_rel_path=normalized_book,
        inbox_book_title=inbox_title,
        generated_at=generated_at,
    )
    payload["updated_at"] = str(existing.get("updated_at", "")).strip() or payload["updated_at"]
    raw_rows = existing.get("decisions", [])
    if isinstance(raw_rows, list):
        payload["decisions"] = _merge_context_review_decisions([], [row for row in raw_rows if isinstance(row, dict)])
    return payload


def _status_from_metrics(metrics: dict[str, int]) -> str:
    if metrics["critical_open"] > 0 or metrics["major_open"] > 0:
        return "blocked"
    return "approved"


def _finding_id(stage: str, page_number: int, field: str, category: str) -> str:
    return f"{stage}-p{page_number:02d}-{field}-{category}".replace(" ", "-").lower()


def _empty_metrics() -> dict[str, int]:
    return {
        "critical_open": 0,
        "major_open": 0,
        "minor_open": 0,
        "info_open": 0,
    }


def _compute_metrics(findings: list[dict[str, Any]]) -> dict[str, int]:
    metrics = _empty_metrics()
    for finding in findings:
        if str(finding.get("decision", "pending")).strip().lower() not in OPEN_FINDING_DECISIONS:
            continue
        severity = str(finding.get("severity", "")).strip().lower()
        if severity == "critical":
            metrics["critical_open"] += 1
        elif severity == "major":
            metrics["major_open"] += 1
        elif severity == "minor":
            metrics["minor_open"] += 1
        else:
            metrics["info_open"] += 1
    return metrics


def _contains_mojibake(text: str) -> bool:
    # Buscar secuencias típicas de mojibake sin dejar caracteres rotos literales en el código.
    return any(token in text for token in ("\u00c3", "\u00c2", "\ufffd"))


def _try_fix_mojibake(value: str) -> str:
    text = value
    for _ in range(2):
        if not _contains_mojibake(text):
            break
        try:
            repaired = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if repaired == text:
            break
        text = repaired
    return text


def _extract_story_title(markdown: str, fallback: str) -> str:
    match = re.search(r"^\s*#\s+(.+?)\s*$", markdown, flags=re.MULTILINE)
    if not match:
        return fallback
    return match.group(1).strip() or fallback


def _extract_page_sections(markdown: str) -> list[tuple[int, str]]:
    header_re = re.compile(
        r"^\s*##\s*P(?:a|á)?.*?(\d+)\s*(?:</h2>)?\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    matches = list(header_re.finditer(markdown))
    sections: list[tuple[int, str]] = []
    for index, match in enumerate(matches):
        try:
            page_number = int(match.group(1))
        except (TypeError, ValueError):
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        sections.append((page_number, body))
    sections.sort(key=lambda item: item[0])
    return sections


def _extract_field_block(section: str, label: str) -> str:
    pattern = re.compile(
        rf"{re.escape(label)}\s*:\s*```(?:text)?[ \t]*\r?\n(.*?)\r?\n```",
        flags=re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(section)
    if match:
        return match.group(1).strip()
    fallback_pattern = re.compile(
        rf"^\s*{re.escape(label)}\s*:\s*(.*)$",
        flags=re.IGNORECASE,
    )
    fallback = fallback_pattern.search(section)
    return fallback.group(1).strip() if fallback else ""


def _parse_story_markdown(md_path: Path) -> dict[str, Any]:
    markdown = _safe_read_markdown(md_path)
    story_id = md_path.stem
    title = _extract_story_title(markdown, fallback=f"Cuento {story_id}")
    sections = _extract_page_sections(markdown)
    if not sections:
        raise EditorialOrquestadorError(
            f"No se detectaron páginas en {md_path}. Se esperaba '## Página NN'."
        )

    pages: list[dict[str, Any]] = []
    seen_pages: set[int] = set()
    for page_number, section in sections:
        if page_number in seen_pages:
            continue
        seen_pages.add(page_number)
        text_original = _extract_field_block(section, "Texto")
        prompt_original = _extract_field_block(section, "Imagen")
        pages.append(
            {
                "page_number": page_number,
                "status": "draft",
                "text": {
                    "original": text_original,
                    "current": text_original,
                },
                "images": {
                    "main": {
                        "status": "draft",
                        "prompt": {
                            "original": prompt_original,
                            "current": prompt_original,
                        },
                        "active_id": "",
                        "alternatives": [],
                    }
                },
            }
        )

    pages.sort(key=lambda item: int(item["page_number"]))
    return {
        "story_id": story_id,
        "title": title,
        "pages": pages,
    }


def discover_inbox_stories(*, inbox_book_title: str, book_rel_path: str) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    book_rel_path = _validate_book_rel_path(book_rel_path)
    inbox_root = (LIBRARY_ROOT / "_inbox" / inbox_book_title).resolve()
    if not inbox_root.exists() or not inbox_root.is_dir():
        raise EditorialOrquestadorError(f"No existe el libro en inbox: {inbox_root}")

    candidates: dict[str, list[dict[str, Any]]] = {}
    ignored_items: list[dict[str, Any]] = []
    for md_path in sorted(inbox_root.rglob("*.md"), key=lambda item: item.as_posix()):
        if not _looks_like_story_md(md_path):
            continue
        story_id = md_path.stem
        rel_to_book = md_path.resolve().relative_to(inbox_root).as_posix()
        parts = Path(rel_to_book).parts[:-1]
        in_ignore = "_ignore" in parts
        is_root = "/" not in rel_to_book

        item = {
            "story_id": story_id,
            "source_md_rel": _to_project_rel(md_path),
            "source_md_abs": str(md_path.resolve()),
            "source_book_rel": rel_to_book,
            "is_root": is_root,
            "in_ignore": in_ignore,
        }
        candidates.setdefault(story_id, []).append(item)

    selected: list[dict[str, Any]] = []
    no_touch_existing: list[dict[str, Any]] = []
    for story_id, items in sorted(candidates.items(), key=lambda entry: entry[0]):
        non_ignored = [item for item in items if not item["in_ignore"]]
        if non_ignored:
            root_candidates = [item for item in non_ignored if item["is_root"]]
            if root_candidates:
                chosen = sorted(root_candidates, key=lambda row: row["source_md_rel"])[0]
                chosen["selection_reason"] = "root_priority"
                selected.append(chosen)
                for dropped in items:
                    if dropped["source_md_rel"] == chosen["source_md_rel"]:
                        continue
                    reason = "duplicate_ignored_by_root_priority"
                    ignored_items.append(
                        {
                            "story_id": story_id,
                            "source_md_rel": dropped["source_md_rel"],
                            "reason": reason,
                        }
                    )
            else:
                chosen = sorted(non_ignored, key=lambda row: row["source_md_rel"])[0]
                chosen["selection_reason"] = "single_or_first_non_root"
                selected.append(chosen)
                for dropped in items:
                    if dropped["source_md_rel"] == chosen["source_md_rel"]:
                        continue
                    reason = (
                        "ignored_subpath_rule"
                        if dropped["in_ignore"]
                        else "duplicate_ignored_non_root_priority"
                    )
                    ignored_items.append(
                        {
                            "story_id": story_id,
                            "source_md_rel": dropped["source_md_rel"],
                            "reason": reason,
                        }
                    )
        else:
            for dropped in items:
                ignored_items.append(
                    {
                        "story_id": story_id,
                        "source_md_rel": dropped["source_md_rel"],
                        "reason": "inside_ignore_folder",
                    }
                )
            existing_json = LIBRARY_ROOT / _normalize_rel_path(book_rel_path) / f"{story_id}.json"
            if existing_json.exists():
                no_touch_existing.append(
                    {
                        "story_id": story_id,
                        "story_rel_path": f"{_normalize_rel_path(book_rel_path)}/{story_id}",
                        "json_rel_path": _to_project_rel(existing_json),
                        "reason": "no_touch_existing_source_in_ignore",
                    }
                )

    selected.sort(key=lambda row: row["story_id"])
    return {
        "inbox_book_title": inbox_book_title,
        "book_rel_path": book_rel_path,
        "source_root_rel": _to_project_rel(inbox_root),
        "selected_stories": selected,
        "ignored_items": ignored_items,
        "no_touch_existing": no_touch_existing,
    }


def _build_story_payload_for_ingest(
    *,
    source_md_path: Path,
    story_id: str,
    book_rel_path: str,
    existing_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    parsed = _parse_story_markdown(source_md_path)
    now_iso = _utc_now_iso()
    created_at = now_iso
    if existing_payload:
        created_at = str(existing_payload.get("created_at", "")).strip() or now_iso
    return {
        "schema_version": "1.0",
        "story_id": story_id,
        "title": parsed["title"],
        "status": "draft",
        "book_rel_path": _normalize_rel_path(book_rel_path),
        "created_at": created_at,
        "updated_at": now_iso,
        "pages": parsed["pages"],
    }


def _write_pipeline_state(book_rel_path: str, state_payload: dict[str, Any]) -> Path:
    paths = _review_paths(book_rel_path, "00")
    target = paths["pipeline_state_json"]
    _write_json(target, state_payload)
    return target


def run_ingesta_json(*, inbox_book_title: str, book_rel_path: str) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    book_rel_path = _validate_book_rel_path(book_rel_path)
    discovery = discover_inbox_stories(inbox_book_title=inbox_book_title, book_rel_path=book_rel_path)
    selected = discovery["selected_stories"]
    ingestion_rows: list[dict[str, Any]] = []

    for row in selected:
        story_id = row["story_id"]
        story_rel_path = f"{_normalize_rel_path(book_rel_path)}/{story_id}"
        source_md_path = Path(row["source_md_abs"])
        existing_payload: dict[str, Any] | None = None
        try:
            existing_payload = load_story(story_rel_path)
        except (FileNotFoundError, StoryStoreError):
            existing_payload = None

        payload = _build_story_payload_for_ingest(
            source_md_path=source_md_path,
            story_id=story_id,
            book_rel_path=book_rel_path,
            existing_payload=existing_payload,
        )
        saved = save_story_payload(story_rel_path=story_rel_path, payload=payload, touch_updated_at=True)
        ingestion_rows.append(
            {
                "story_id": story_id,
                "story_rel_path": story_rel_path,
                "source_md_rel": row["source_md_rel"],
                "pages": len(saved.get("pages", [])),
                "result": "updated" if existing_payload else "created",
            }
        )

    state_payload = {
        "schema_version": PIPELINE_SCHEMA_VERSION,
        "pipeline": "editorial_orquestador",
        "phase": "ingested",
        "generated_at": _utc_now_iso(),
        "book_rel_path": _normalize_rel_path(book_rel_path),
        "inbox_book_title": inbox_book_title,
        "source_inventory": {
            "selected_stories": selected,
            "ignored_items": discovery["ignored_items"],
            "no_touch_existing": discovery["no_touch_existing"],
        },
        "ingestion": ingestion_rows,
        "stories": [
            {
                "story_id": row["story_id"],
                "story_rel_path": row["story_rel_path"],
                "status": "draft",
                "text_stage": None,
                "prompt_stage": None,
            }
            for row in ingestion_rows
        ],
        "totals": {
            "selected": len(selected),
            "ingested": len(ingestion_rows),
            "critical_open": 0,
            "major_open": 0,
            "minor_open": 0,
            "info_open": 0,
        },
    }
    pipeline_state_path = _write_pipeline_state(book_rel_path, state_payload)
    state_payload["pipeline_state_rel"] = _to_project_rel(pipeline_state_path)
    return state_payload


def _build_finding(
    *,
    stage: str,
    severity: str,
    category: str,
    page_number: int,
    field: str,
    evidence: str,
    suggestions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": _finding_id(stage, page_number, field, category),
        "severity": severity,
        "category": category,
        "page_number": int(page_number),
        "field": field,
        "evidence": evidence.strip(),
        "suggestions": suggestions,
        "decision": "pending",
    }


def _prompt_is_structured(prompt_value: str) -> bool:
    labels_found: set[str] = set()
    for line in prompt_value.splitlines():
        if ":" not in line:
            continue
        label = line.split(":", 1)[0].strip().upper()
        labels_found.add(label)
    return all(label in labels_found for label in PROMPT_STRUCTURED_LABELS)


def _short_sentence(text_value: str, fallback: str) -> str:
    cleaned = re.sub(r"\s+", " ", text_value).strip()
    if not cleaned:
        return fallback
    sentence = re.split(r"[.!?]", cleaned)[0].strip()
    if not sentence:
        sentence = cleaned
    return sentence[:160]


def _structured_prompt_v1(*, page_text: str, base_prompt: str) -> str:
    subject = _short_sentence(page_text, "Personaje principal de la página.")
    scene = _short_sentence(base_prompt, "Escena clave del cuento con foco narrativo.")
    continuity = _short_sentence(page_text, "Mantener continuidad con las páginas vecinas.")
    return "\n".join(
        [
            f"SUJETO: {subject}",
            f"ESCENA: {scene}",
            "ESTILO: Ilustracion narrativa infantil coherente con Cosmere.",
            "COMPOSICION: Plano medio, lectura clara y foco en accion principal.",
            "ILUMINACION_COLOR: Paleta ceniza rojiza con contraste suave.",
            f"CONTINUIDAD: {continuity}",
            "RESTRICCIONES: Sin texto incrustado, sin marcas de agua, anatomía consistente.",
        ]
    )


def _audit_text_findings(story_payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for page in story_payload.get("pages", []):
        page_number = int(page.get("page_number", 0))
        text_block = page.get("text", {})
        text_current = str(text_block.get("current", "")).strip()
        text_original = str(text_block.get("original", "")).strip()

        if not text_current:
            suggestions = [
                {
                    "id": "A",
                    "label": "Usar texto original",
                    "proposed_value": text_original,
                },
                {
                    "id": "B",
                    "label": "Placeholder editorial",
                    "proposed_value": "Texto pendiente de revision editorial.",
                },
                {
                    "id": "C",
                    "label": "Mantener vacío",
                    "proposed_value": "",
                },
            ]
            findings.append(
                _build_finding(
                    stage=STAGE_TEXT_AUDIT,
                    severity="critical",
                    category="missing_text",
                    page_number=page_number,
                    field="text.current",
                    evidence="La página no tiene texto actual.",
                    suggestions=suggestions,
                )
            )
            continue

        if _contains_mojibake(text_current):
            repaired = _try_fix_mojibake(text_current)
            suggestions = [
                {
                    "id": "A",
                    "label": "Aplicar reparación de codificación",
                    "proposed_value": repaired,
                },
                {
                    "id": "B",
                    "label": "Revertir a texto original",
                    "proposed_value": text_original,
                },
                {
                    "id": "C",
                    "label": "Mantener texto actual",
                    "proposed_value": text_current,
                },
            ]
            findings.append(
                _build_finding(
                    stage=STAGE_TEXT_AUDIT,
                    severity="major",
                    category="encoding_mojibake",
                    page_number=page_number,
                    field="text.current",
                    evidence="Se detectaron caracteres mojibake en texto.current.",
                    suggestions=suggestions,
                )
            )

        if re.search(r"\s{2,}", text_current):
            suggestions = [
                {
                    "id": "A",
                    "label": "Normalizar espacios dobles",
                    "proposed_value": re.sub(r"\s{2,}", " ", text_current),
                },
                {
                    "id": "B",
                    "label": "Revertir a texto original",
                    "proposed_value": text_original,
                },
                {
                    "id": "C",
                    "label": "Mantener texto actual",
                    "proposed_value": text_current,
                },
            ]
            findings.append(
                _build_finding(
                    stage=STAGE_TEXT_AUDIT,
                    severity="minor",
                    category="spacing_cleanup",
                    page_number=page_number,
                    field="text.current",
                    evidence="Se detectaron espacios dobles o múltiples.",
                    suggestions=suggestions,
                )
            )

    return findings


def _audit_prompt_findings(story_payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for page in story_payload.get("pages", []):
        page_number = int(page.get("page_number", 0))
        text_current = str(page.get("text", {}).get("current", "")).strip()
        images = page.get("images", {})
        main_prompt = str(images.get("main", {}).get("prompt", {}).get("current", "")).strip()
        original_prompt = str(images.get("main", {}).get("prompt", {}).get("original", "")).strip()

        if not main_prompt:
            suggestions = [
                {
                    "id": "A",
                    "label": "Generar prompt estructurado v1 desde texto",
                    "proposed_value": _structured_prompt_v1(page_text=text_current, base_prompt=original_prompt),
                },
                {
                    "id": "B",
                    "label": "Usar prompt original",
                    "proposed_value": original_prompt,
                },
                {
                    "id": "C",
                    "label": "Mantener vacío",
                    "proposed_value": "",
                },
            ]
            findings.append(
                _build_finding(
                    stage=STAGE_PROMPT_AUDIT,
                    severity="critical",
                    category="missing_prompt",
                    page_number=page_number,
                    field="images.main.prompt.current",
                    evidence="El prompt main actual está vacío.",
                    suggestions=suggestions,
                )
            )
            continue

        if _contains_mojibake(main_prompt):
            repaired = _try_fix_mojibake(main_prompt)
            suggestions = [
                {
                    "id": "A",
                    "label": "Aplicar reparación de codificación",
                    "proposed_value": repaired,
                },
                {
                    "id": "B",
                    "label": "Revertir a prompt original",
                    "proposed_value": original_prompt,
                },
                {
                    "id": "C",
                    "label": "Mantener prompt actual",
                    "proposed_value": main_prompt,
                },
            ]
            findings.append(
                _build_finding(
                    stage=STAGE_PROMPT_AUDIT,
                    severity="major",
                    category="encoding_mojibake",
                    page_number=page_number,
                    field="images.main.prompt.current",
                    evidence="Se detectaron caracteres mojibake en prompt.current.",
                    suggestions=suggestions,
                )
            )

        if not _prompt_is_structured(main_prompt):
            structured = _structured_prompt_v1(page_text=text_current, base_prompt=main_prompt)
            suggestions = [
                {
                    "id": "A",
                    "label": "Convertir a plantilla estructurada v1",
                    "proposed_value": structured,
                },
                {
                    "id": "B",
                    "label": "Estructurada v1 desde original",
                    "proposed_value": _structured_prompt_v1(page_text=text_current, base_prompt=original_prompt),
                },
                {
                    "id": "C",
                    "label": "Mantener prompt actual",
                    "proposed_value": main_prompt,
                },
            ]
            findings.append(
                _build_finding(
                    stage=STAGE_PROMPT_AUDIT,
                    severity="major",
                    category="missing_structured_v1",
                    page_number=page_number,
                    field="images.main.prompt.current",
                    evidence="El prompt no cumple la plantilla estructurada v1.",
                    suggestions=suggestions,
                )
            )

    return findings


def _sync_decisions_file(
    *,
    book_rel_path: str,
    story_id: str,
    story_rel_path: str,
    stage: str,
    findings: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    paths = _review_paths(book_rel_path, story_id)
    existing = _read_json(paths["decisions_json"]) or {}
    existing_rows = existing.get("decisions", []) if isinstance(existing.get("decisions", []), list) else []

    decision_by_id: dict[str, dict[str, Any]] = {}
    for row in existing_rows:
        if not isinstance(row, dict):
            continue
        finding_id = str(row.get("finding_id", "")).strip()
        if not finding_id:
            continue
        decision_by_id[finding_id] = {
            "finding_id": finding_id,
            "decision": str(row.get("decision", "pending")).strip().lower() or "pending",
            "selected_option": str(row.get("selected_option", "")).strip().upper(),
            "notes": str(row.get("notes", "")),
        }

    output_rows: list[dict[str, Any]] = []
    for finding in findings:
        finding_id = str(finding["id"])
        existing_item = decision_by_id.get(finding_id)
        if existing_item:
            output_rows.append(existing_item)
        else:
            output_rows.append(
                {
                    "finding_id": finding_id,
                    "decision": "pending",
                    "selected_option": "",
                    "notes": "",
                }
            )

    payload = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "story_rel_path": story_rel_path,
        "story_id": story_id,
        "stage": stage,
        "updated_at": _utc_now_iso(),
        "decisions": output_rows,
    }
    _write_json(paths["decisions_json"], payload)
    return {row["finding_id"]: row for row in output_rows}


def _merge_decisions(findings: list[dict[str, Any]], decision_map: dict[str, dict[str, Any]]) -> None:
    for finding in findings:
        finding_id = str(finding["id"])
        row = decision_map.get(finding_id)
        if not row:
            finding["decision"] = "pending"
            finding["selected_option"] = ""
            continue
        decision = str(row.get("decision", "pending")).strip().lower() or "pending"
        if decision not in {"pending", "accepted", "rejected"}:
            decision = "pending"
        finding["decision"] = decision
        finding["selected_option"] = str(row.get("selected_option", "")).strip().upper()


def _apply_selected_suggestions(
    *,
    story_payload: dict[str, Any],
    findings: list[dict[str, Any]],
) -> bool:
    changed = False
    page_by_number = {int(page.get("page_number", 0)): page for page in story_payload.get("pages", [])}

    for finding in findings:
        if str(finding.get("decision", "")).strip().lower() != "accepted":
            continue
        selected_option = str(finding.get("selected_option", "")).strip().upper()
        if not selected_option:
            continue
        suggestion = next(
            (
                item
                for item in finding.get("suggestions", [])
                if str(item.get("id", "")).strip().upper() == selected_option
            ),
            None,
        )
        if not suggestion:
            continue
        page_number = int(finding.get("page_number", 0))
        page = page_by_number.get(page_number)
        if not page:
            continue
        field = str(finding.get("field", ""))
        proposed = str(suggestion.get("proposed_value", ""))

        if field == "text.current":
            text_block = page.setdefault("text", {"original": "", "current": ""})
            if str(text_block.get("current", "")) != proposed:
                text_block["current"] = proposed
                changed = True
        elif field == "images.main.prompt.current":
            images = page.setdefault("images", {})
            main = images.setdefault(
                "main",
                {
                    "status": "draft",
                    "prompt": {"original": "", "current": ""},
                    "active_id": "",
                    "alternatives": [],
                },
            )
            prompt = main.setdefault("prompt", {"original": "", "current": ""})
            if str(prompt.get("current", "")) != proposed:
                prompt["current"] = proposed
                changed = True
        elif field == "images.secondary.prompt.current":
            images = page.setdefault("images", {})
            secondary = images.setdefault(
                "secondary",
                {
                    "status": "draft",
                    "prompt": {"original": "", "current": ""},
                    "active_id": "",
                    "alternatives": [],
                },
            )
            prompt = secondary.setdefault("prompt", {"original": "", "current": ""})
            if str(prompt.get("current", "")) != proposed:
                prompt["current"] = proposed
                changed = True

    return changed


def _review_markdown(review_payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Review {review_payload['story_id']} - {review_payload['stage']}")
    lines.append("")
    lines.append(f"- Story: `{review_payload['story_rel_path']}`")
    lines.append(f"- Status: `{review_payload['status']}`")
    lines.append(f"- Generated at: `{review_payload['generated_at']}`")
    lines.append("")
    metrics = review_payload.get("metrics", {})
    lines.append("## Metrics")
    lines.append("")
    lines.append(f"- critical_open: `{metrics.get('critical_open', 0)}`")
    lines.append(f"- major_open: `{metrics.get('major_open', 0)}`")
    lines.append(f"- minor_open: `{metrics.get('minor_open', 0)}`")
    lines.append(f"- info_open: `{metrics.get('info_open', 0)}`")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    findings = review_payload.get("findings", [])
    if not findings:
        lines.append("- Sin hallazgos.")
        lines.append("")
        return "\n".join(lines)

    for finding in findings:
        lines.append(
            f"- [{finding['severity']}] `{finding['id']}` p{int(finding['page_number']):02d} `{finding['field']}`"
        )
        lines.append(f"  evidencia: {finding['evidence']}")
        lines.append(
            f"  decision: {finding.get('decision', 'pending')} | opción: {finding.get('selected_option', '') or '-'}"
        )
        suggestions = finding.get("suggestions", [])
        if suggestions:
            for item in suggestions:
                preview = str(item.get("proposed_value", "")).strip().replace("\n", " ")
                if len(preview) > 120:
                    preview = preview[:117] + "..."
                lines.append(f"  - {item.get('id', '?')}: {item.get('label', '')} -> `{preview}`")
        lines.append("")
    return "\n".join(lines)


def _process_review_stage(
    *,
    book_rel_path: str,
    story_id: str,
    stage: str,
    apply_decisions: bool,
) -> dict[str, Any]:
    story_rel_path = f"{_normalize_rel_path(book_rel_path)}/{story_id}"
    story_payload = load_story(story_rel_path)

    if stage == STAGE_TEXT_AUDIT:
        findings = _audit_text_findings(story_payload)
    elif stage == STAGE_PROMPT_AUDIT:
        findings = _audit_prompt_findings(story_payload)
    else:
        raise EditorialOrquestadorError(f"Etapa no soportada: {stage}")

    decisions_map = _sync_decisions_file(
        book_rel_path=book_rel_path,
        story_id=story_id,
        story_rel_path=story_rel_path,
        stage=stage,
        findings=findings,
    )
    _merge_decisions(findings, decisions_map)

    changed = False
    if apply_decisions:
        changed = _apply_selected_suggestions(story_payload=story_payload, findings=findings)
        if changed:
            save_story_payload(story_rel_path=story_rel_path, payload=story_payload, touch_updated_at=True)
            story_payload = load_story(story_rel_path)
            if stage == STAGE_TEXT_AUDIT:
                findings = _audit_text_findings(story_payload)
            else:
                findings = _audit_prompt_findings(story_payload)
            decisions_map = _sync_decisions_file(
                book_rel_path=book_rel_path,
                story_id=story_id,
                story_rel_path=story_rel_path,
                stage=stage,
                findings=findings,
            )
            _merge_decisions(findings, decisions_map)

    metrics = _compute_metrics(findings)
    review_payload = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "story_rel_path": story_rel_path,
        "story_id": story_id,
        "stage": stage,
        "status": _status_from_metrics(metrics),
        "generated_at": _utc_now_iso(),
        "findings": findings,
        "metrics": metrics,
    }

    paths = _review_paths(book_rel_path, story_id)
    _write_json(paths["review_json"], review_payload)
    paths["review_md"].write_text(_review_markdown(review_payload), encoding="utf-8")

    return {
        "story_id": story_id,
        "story_rel_path": story_rel_path,
        "stage": stage,
        "status": review_payload["status"],
        "metrics": metrics,
        "findings": len(findings),
        "applied_changes": bool(changed),
        "review_json_rel": _to_project_rel(paths["review_json"]),
        "review_md_rel": _to_project_rel(paths["review_md"]),
        "decisions_json_rel": _to_project_rel(paths["decisions_json"]),
    }


def run_text_audit(*, book_rel_path: str, story_id: str) -> dict[str, Any]:
    return _process_review_stage(
        book_rel_path=book_rel_path,
        story_id=story_id,
        stage=STAGE_TEXT_AUDIT,
        apply_decisions=False,
    )


def run_text_correction(*, book_rel_path: str, story_id: str) -> dict[str, Any]:
    summary = _process_review_stage(
        book_rel_path=book_rel_path,
        story_id=story_id,
        stage=STAGE_TEXT_AUDIT,
        apply_decisions=True,
    )
    if summary["status"] == "blocked":
        set_story_status(story_rel_path=summary["story_rel_path"], status="text_blocked")
    else:
        set_story_status(story_rel_path=summary["story_rel_path"], status="text_reviewed")
    return summary


def run_prompt_audit(*, book_rel_path: str, story_id: str) -> dict[str, Any]:
    return _process_review_stage(
        book_rel_path=book_rel_path,
        story_id=story_id,
        stage=STAGE_PROMPT_AUDIT,
        apply_decisions=False,
    )


def run_prompt_correction(*, book_rel_path: str, story_id: str) -> dict[str, Any]:
    summary = _process_review_stage(
        book_rel_path=book_rel_path,
        story_id=story_id,
        stage=STAGE_PROMPT_AUDIT,
        apply_decisions=True,
    )
    if summary["status"] == "blocked":
        set_story_status(story_rel_path=summary["story_rel_path"], status="prompt_blocked")
    else:
        set_story_status(story_rel_path=summary["story_rel_path"], status="prompt_reviewed")
    return summary


def _context_file_candidates(node_abs: Path) -> list[Path]:
    names = ("meta.md", "anclas.md", "glosario.md", "canon.md", "contexto.md")
    rows: list[Path] = []
    for name in names:
        file_obj = node_abs / name
        if file_obj.exists() and file_obj.is_file():
            rows.append(file_obj)
    return rows


def _parse_markdown_glossary(markdown: str, *, source_rel: str, priority: int) -> list[dict[str, Any]]:
    lines = markdown.splitlines()
    header_idx = -1
    for index, line in enumerate(lines):
        if "glosario" in line.strip().lower():
            header_idx = index
            break
    if header_idx < 0:
        return []

    entries: list[dict[str, Any]] = []
    for raw in lines[header_idx + 1 :]:
        line = raw.strip()
        if not line.startswith("|") or line.count("|") < 5:
            if entries:
                break
            continue
        cols = [part.strip() for part in line.strip("|").split("|")]
        if len(cols) < 5:
            continue
        if cols[0].lower() in {"termino", "término", "---", ""}:
            continue
        entries.append(
            {
                "term": cols[0],
                "canonical": cols[1] or cols[0],
                "allowed": [item.strip() for item in re.split(r"[;,]", cols[2]) if item.strip()],
                "forbidden": [item.strip() for item in re.split(r"[;,]", cols[3]) if item.strip()],
                "notes": cols[4],
                "source_rel": source_rel,
                "priority": int(priority),
            }
        )
    return entries


def _discover_canonical_pdfs(inbox_book_title: str) -> dict[str, Any]:
    inbox_root = (LIBRARY_ROOT / "_inbox" / inbox_book_title).resolve()
    if not inbox_root.exists() or not inbox_root.is_dir():
        return {
            "source_root_rel": "",
            "canonical_pdf_rel_paths": [],
            "story_pdf_by_id": {},
        }

    rel_paths: list[str] = []
    story_pdf_by_id: dict[str, str] = {}
    for pdf_path in sorted(inbox_root.rglob("*.pdf"), key=lambda item: item.as_posix()):
        rel = pdf_path.resolve().relative_to(inbox_root).as_posix()
        if "_ignore" in Path(rel).parts:
            continue
        rel_project = _to_project_rel(pdf_path)
        rel_paths.append(rel_project)
        if re.fullmatch(r"\d{2}\.pdf", pdf_path.name, re.IGNORECASE):
            story_pdf_by_id[pdf_path.stem] = rel_project

    return {
        "source_root_rel": _to_project_rel(inbox_root),
        "canonical_pdf_rel_paths": rel_paths,
        "story_pdf_by_id": story_pdf_by_id,
    }


def run_contexto_canon(*, inbox_book_title: str, book_rel_path: str) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book = _validate_book_rel_path(book_rel_path)
    parts = [part for part in normalized_book.split("/") if part]
    node_chain = ["/".join(parts[:idx]) for idx in range(1, len(parts) + 1)]

    chain_rows: list[dict[str, Any]] = []
    glossary_map: dict[str, dict[str, Any]] = {}
    for priority, node_rel in enumerate(node_chain, start=1):
        node_abs = (LIBRARY_ROOT / node_rel).resolve()
        if not node_abs.exists() or not node_abs.is_dir():
            continue
        file_rows: list[dict[str, Any]] = []
        for file_obj in _context_file_candidates(node_abs):
            rel_project = _to_project_rel(file_obj)
            markdown = file_obj.read_text(encoding="utf-8", errors="replace")
            parsed = _parse_markdown_glossary(markdown, source_rel=rel_project, priority=priority)
            for item in parsed:
                glossary_map[str(item["term"]).strip().lower()] = item
            file_rows.append({"file_rel_path": rel_project, "glossary_entries": len(parsed)})
        if file_rows:
            chain_rows.append(
                {
                    "node_rel_path": node_rel,
                    "priority": int(priority),
                    "files": file_rows,
                }
            )

    canonical = _discover_canonical_pdfs(inbox_book_title)
    glossary_base = sorted(glossary_map.values(), key=lambda item: str(item.get("term", "")).lower())
    context_review_payload = _read_context_review_payload(
        book_rel_path=normalized_book,
        inbox_book_title=inbox_book_title,
    )
    context_review_decisions = context_review_payload.get("decisions", [])
    glossary_merged, ignored_missing_term = _apply_context_review_to_glossary(
        glossary_base=glossary_base,
        review_decisions=context_review_decisions if isinstance(context_review_decisions, list) else [],
    )
    context_review_payload["metrics"] = _build_context_review_metrics(
        review_decisions=context_review_decisions if isinstance(context_review_decisions, list) else [],
        ignored_missing_term=ignored_missing_term,
    )
    payload = {
        "schema_version": CASCADE_SCHEMA_VERSION,
        "generated_at": _utc_now_iso(),
        "book_rel_path": normalized_book,
        "inbox_book_title": inbox_book_title,
        "context_chain": chain_rows,
        "canonical_pdfs": canonical,
        "glossary_merged": glossary_merged,
    }
    paths = _review_paths(normalized_book, "00")
    _write_json(paths["context_chain_json"], payload)
    _write_json(
        paths["glossary_merged_json"],
        {
            "schema_version": CASCADE_SCHEMA_VERSION,
            "generated_at": _utc_now_iso(),
            "book_rel_path": normalized_book,
            "inbox_book_title": inbox_book_title,
            "glossary_merged": glossary_merged,
        },
    )
    payload["context_review"] = context_review_payload
    payload["context_chain_rel"] = _to_project_rel(paths["context_chain_json"])
    payload["glossary_merged_rel"] = _to_project_rel(paths["glossary_merged_json"])
    payload["context_review_rel"] = (
        _to_project_rel(paths["context_review_json"]) if paths["context_review_json"].exists() else ""
    )
    return payload


def run_contexto_revision_glosario(
    *,
    inbox_book_title: str,
    book_rel_path: str,
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    inbox_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book = _validate_book_rel_path(book_rel_path)
    if not isinstance(decisions, list):
        raise EditorialOrquestadorError("`decisions` debe ser una lista de objetos de revisión.")

    current_context = run_contexto_canon(inbox_book_title=inbox_title, book_rel_path=normalized_book)
    existing_review = _read_context_review_payload(book_rel_path=normalized_book, inbox_book_title=inbox_title)
    existing_decisions = existing_review.get("decisions", [])
    merged_decisions = _merge_context_review_decisions(
        existing_decisions if isinstance(existing_decisions, list) else [],
        [row for row in decisions if isinstance(row, dict)],
    )

    glossary_rows = current_context.get("glossary_merged", [])
    glossary_keys = {
        str(item.get("term", "")).strip().lower()
        for item in glossary_rows
        if isinstance(item, dict) and str(item.get("term", "")).strip()
    }
    ignored_missing_term = sum(
        1 for row in merged_decisions if str(row.get("term_key", "")).strip().lower() not in glossary_keys
    )
    payload = _context_review_payload_base(
        book_rel_path=normalized_book,
        inbox_book_title=inbox_title,
        generated_at=str(existing_review.get("generated_at", "")).strip() or _utc_now_iso(),
    )
    payload["decisions"] = merged_decisions
    payload["metrics"] = _build_context_review_metrics(
        review_decisions=merged_decisions,
        ignored_missing_term=ignored_missing_term,
    )

    paths = _review_paths(normalized_book, "00")
    _write_json(paths["context_review_json"], payload)
    refreshed = run_contexto_canon(inbox_book_title=inbox_title, book_rel_path=normalized_book)
    refreshed["context_review"] = payload
    refreshed["context_review_rel"] = _to_project_rel(paths["context_review_json"])
    return refreshed


def _reference_rows(*, canonical_story_pdf_rel: str, context_payload: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if canonical_story_pdf_rel:
        rows.append({"type": "canonical_pdf", "path": canonical_story_pdf_rel})
    for chain_row in context_payload.get("context_chain", []):
        for file_row in chain_row.get("files", []):
            rows.append({"type": "context_file", "path": str(file_row.get("file_rel_path", ""))})
    return rows


def _text_drift_ratio(original: str, current: str) -> float:
    original_tokens = re.findall(r"\w+", original.lower())
    current_tokens = re.findall(r"\w+", current.lower())
    if not original_tokens:
        return 0.0
    overlap = len(set(original_tokens).intersection(set(current_tokens)))
    return 1.0 - (overlap / max(len(set(original_tokens)), 1))


def _findings_for_stage(
    *,
    stage: str,
    story_payload: dict[str, Any],
    canonical_story_pdf_rel: str,
    context_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    if stage == STAGE_TEXT:
        findings = _audit_text_findings(story_payload)
        glossary = context_payload.get("glossary_merged", [])
        for page in story_payload.get("pages", []):
            page_number = int(page.get("page_number", 0))
            text_original = str(page.get("text", {}).get("original", "")).strip()
            text_current = str(page.get("text", {}).get("current", "")).strip()
            if text_original and text_current:
                drift = _text_drift_ratio(text_original, text_current)
                if drift >= 0.80:
                    findings.append(
                        _build_finding(
                            stage=STAGE_TEXT_AUDIT,
                            severity="major",
                            category="semantic_drift_proxy",
                            page_number=page_number,
                            field="text.current",
                                evidence=f"Desvío alto respecto al texto base (ratio={drift:.2f}).",
                            suggestions=[
                                {"id": "A", "label": "Revertir a original", "proposed_value": text_original},
                                {"id": "B", "label": "Mantener actual", "proposed_value": text_current},
                                {
                                    "id": "C",
                                    "label": "Reducir desvío",
                                    "proposed_value": text_current[: max(len(text_current) // 2, 1)],
                                },
                            ],
                        )
                    )
            for entry in glossary:
                for token in entry.get("forbidden", []):
                    forbidden = str(token).strip().lower()
                    if forbidden and forbidden in text_current.lower():
                        findings.append(
                            _build_finding(
                                stage=STAGE_TEXT_AUDIT,
                                severity="critical",
                                category="glossary_forbidden_term",
                                page_number=page_number,
                                field="text.current",
                                evidence=f"Uso de término prohibido por glosario: '{forbidden}'.",
                                suggestions=[
                                    {
                                        "id": "A",
                                        "label": "Sustituir por término preferido",
                                        "proposed_value": text_current.replace(
                                            forbidden,
                                            str(
                                                entry.get(
                                                    "replacement_target",
                                                    entry.get("canonical", forbidden),
                                                )
                                            ),
                                        ),
                                    },
                                    {"id": "B", "label": "Revertir a original", "proposed_value": text_original},
                                    {"id": "C", "label": "Mantener actual", "proposed_value": text_current},
                                ],
                            )
                        )
    else:
        findings = _audit_prompt_findings(story_payload)

    refs = _reference_rows(canonical_story_pdf_rel=canonical_story_pdf_rel, context_payload=context_payload)
    for finding in findings:
        finding["references"] = refs
        sev = str(finding.get("severity", "")).strip().lower()
        finding["impact"] = "Alto" if sev in {"critical", "major"} else "Medio" if sev == "minor" else "Bajo"
    return findings


def _filter_findings_by_severity(findings: list[dict[str, Any]], severity_band: str) -> list[dict[str, Any]]:
    target = severity_band.strip().lower()
    return [item for item in findings if str(item.get("severity", "")).strip().lower() == target]


def _normalize_choice_decision(raw_value: str) -> str:
    value = str(raw_value).strip().lower()
    if value in {"accepted", "rejected", "defer", "pending"}:
        return value
    return "pending"


def _sync_choices_file(
    *,
    book_rel_path: str,
    story_id: str,
    stage: str,
    severity_band: str,
    pass_index: int,
    findings: list[dict[str, Any]],
    auto_decide: bool,
) -> dict[str, dict[str, Any]]:
    story_rel_path = f"{_normalize_rel_path(book_rel_path)}/{story_id}"
    paths = _review_paths(book_rel_path, story_id)
    existing = _read_json(paths["choices_json"]) or {}
    existing_rows = existing.get("choices", []) if isinstance(existing.get("choices", []), list) else []

    existing_map: dict[str, dict[str, Any]] = {}
    for row in existing_rows:
        if not isinstance(row, dict):
            continue
        finding_id = str(row.get("finding_id", "")).strip()
        if not finding_id:
            continue
        existing_map[finding_id] = {
            "finding_id": finding_id,
            "decision": _normalize_choice_decision(str(row.get("decision", "pending"))),
            "selected_option": str(row.get("selected_option", "")).strip().upper(),
            "notes": str(row.get("notes", "")),
        }

    output_rows: list[dict[str, Any]] = []
    for finding in findings:
        finding_id = str(finding.get("id", "")).strip()
        selected = existing_map.get(
            finding_id,
            {"finding_id": finding_id, "decision": "pending", "selected_option": "", "notes": ""},
        )
        # En bandas bloqueantes, `defer` no es válido y se fuerza a pendiente.
        if severity_band in BLOCKING_SEVERITIES and selected["decision"] == "defer":
            selected["decision"] = "pending"
            selected["selected_option"] = ""
            selected["notes"] = "invalid_for_blocking:defer"

        if auto_decide and selected["decision"] == "pending":
            if severity_band in BLOCKING_SEVERITIES:
                selected["decision"] = "accepted"
                selected["selected_option"] = "A"
                selected["notes"] = "auto_policy:blocking_default_A"
            else:
                selected["decision"] = "rejected"
                selected["selected_option"] = ""
                selected["notes"] = "auto_policy:non_blocking_discard"
        output_rows.append(selected)

    payload = {
        "schema_version": CASCADE_SCHEMA_VERSION,
        "story_rel_path": story_rel_path,
        "story_id": story_id,
        "stage": stage,
        "severity_band": severity_band,
        "pass_index": int(pass_index),
        "updated_at": _utc_now_iso(),
        "choices": output_rows,
    }
    _write_json(paths["choices_json"], payload)
    return {row["finding_id"]: row for row in output_rows}


def _merge_choices_into_findings(findings: list[dict[str, Any]], choices_map: dict[str, dict[str, Any]]) -> None:
    for finding in findings:
        row = choices_map.get(str(finding.get("id", "")))
        if not row:
            finding["decision"] = "pending"
            finding["selected_option"] = ""
            continue
        finding["decision"] = _normalize_choice_decision(str(row.get("decision", "pending")))
        finding["selected_option"] = str(row.get("selected_option", "")).strip().upper()
        finding["notes"] = str(row.get("notes", ""))


def _finding_is_open(finding: dict[str, Any], severity_band: str) -> bool:
    decision = _normalize_choice_decision(str(finding.get("decision", "pending")))
    if decision == "accepted":
        return False
    if decision == "rejected":
        return severity_band in BLOCKING_SEVERITIES
    if decision == "defer":
        return severity_band in BLOCKING_SEVERITIES
    return True


def _contrast_alerts_for_stage(
    *,
    stage: str,
    severity_band: str,
    story_payload: dict[str, Any],
    canonical_story_pdf_rel: str,
) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    if stage == STAGE_TEXT:
        for page in story_payload.get("pages", []):
            page_number = int(page.get("page_number", 0))
            text_original = str(page.get("text", {}).get("original", "")).strip()
            text_current = str(page.get("text", {}).get("current", "")).strip()
            drift = _text_drift_ratio(text_original, text_current) if text_original and text_current else 0.0
            if severity_band == "critical" and not text_current:
                alerts.append(
                    {
                        "id": f"contrast-text-critical-p{page_number:02d}",
                        "severity": "critical",
                        "page_number": page_number,
                        "field": "text.current",
                        "evidence": "El texto sigue vacío tras aplicar cambios.",
                        "reference": canonical_story_pdf_rel,
                        "status": "open",
                    }
                )
            if severity_band == "major" and drift >= 0.85:
                alerts.append(
                    {
                        "id": f"contrast-text-major-p{page_number:02d}",
                        "severity": "major",
                        "page_number": page_number,
                        "field": "text.current",
                        "evidence": f"Desvío excesivo frente al canon (ratio={drift:.2f}).",
                        "reference": canonical_story_pdf_rel,
                        "status": "open",
                    }
                )
            if severity_band == "minor" and re.search(r"\s{2,}", text_current):
                alerts.append(
                    {
                        "id": f"contrast-text-minor-p{page_number:02d}",
                        "severity": "minor",
                        "page_number": page_number,
                        "field": "text.current",
                        "evidence": "Persisten espacios multiples.",
                        "reference": canonical_story_pdf_rel,
                        "status": "open",
                    }
                )
    else:
        for page in story_payload.get("pages", []):
            page_number = int(page.get("page_number", 0))
            prompt_current = str(page.get("images", {}).get("main", {}).get("prompt", {}).get("current", "")).strip()
            if severity_band == "critical" and not prompt_current:
                alerts.append(
                    {
                        "id": f"contrast-prompt-critical-p{page_number:02d}",
                        "severity": "critical",
                        "page_number": page_number,
                        "field": "images.main.prompt.current",
                        "evidence": "Prompt principal vacío tras aplicar cambios.",
                        "reference": canonical_story_pdf_rel,
                        "status": "open",
                    }
                )
            if severity_band == "major" and prompt_current and not _prompt_is_structured(prompt_current):
                alerts.append(
                    {
                        "id": f"contrast-prompt-major-p{page_number:02d}",
                        "severity": "major",
                        "page_number": page_number,
                        "field": "images.main.prompt.current",
                        "evidence": "Prompt no cumple estructura v1.",
                        "reference": canonical_story_pdf_rel,
                        "status": "open",
                    }
                )
            if severity_band == "minor" and prompt_current and len(prompt_current) < 24:
                alerts.append(
                    {
                        "id": f"contrast-prompt-minor-p{page_number:02d}",
                        "severity": "minor",
                        "page_number": page_number,
                        "field": "images.main.prompt.current",
                        "evidence": "Prompt demasiado corto para continuidad visual.",
                        "reference": canonical_story_pdf_rel,
                        "status": "open",
                    }
                )
    return alerts


def _append_pass_record(
    *,
    book_rel_path: str,
    story_id: str,
    story_rel_path: str,
    stage: str,
    severity_band: str,
    pass_index: int,
    findings_count: int,
    alerts_open: int,
    applied_changes: bool,
    converged: bool,
    max_passes_reached: bool,
) -> str:
    paths = _review_paths(book_rel_path, story_id)
    existing = _read_json(paths["passes_json"]) or {}
    rows = existing.get("passes", []) if isinstance(existing.get("passes", []), list) else []
    rows.append(
        {
            "stage": stage,
            "severity_band": severity_band,
            "pass_index": int(pass_index),
            "findings_count": int(findings_count),
            "alerts_open": int(alerts_open),
            "applied_changes": bool(applied_changes),
            "converged": bool(converged),
            "max_passes_reached": bool(max_passes_reached),
            "generated_at": _utc_now_iso(),
        }
    )
    _write_json(
        paths["passes_json"],
        {
            "schema_version": CASCADE_SCHEMA_VERSION,
            "story_rel_path": story_rel_path,
            "story_id": story_id,
            "passes": rows,
            "updated_at": _utc_now_iso(),
        },
    )
    return _to_project_rel(paths["passes_json"])


def _write_legacy_sidecars(
    *,
    book_rel_path: str,
    story_id: str,
    story_rel_path: str,
    stage: str,
    findings: list[dict[str, Any]],
    severity_band: str,
    pass_index: int,
) -> None:
    metrics = _compute_metrics(findings)
    stage_name = STAGE_TEXT_AUDIT if stage == STAGE_TEXT else STAGE_PROMPT_AUDIT
    review_payload = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "story_rel_path": story_rel_path,
        "story_id": story_id,
        "stage": stage_name,
        "status": _status_from_metrics(metrics),
        "generated_at": _utc_now_iso(),
        "severity_band": severity_band,
        "pass_index": int(pass_index),
        "findings": findings,
        "metrics": metrics,
    }
    paths = _review_paths(book_rel_path, story_id)
    _write_json(paths["review_json"], review_payload)
    paths["review_md"].write_text(_review_markdown(review_payload), encoding="utf-8")
    _write_json(
        paths["decisions_json"],
        {
            "schema_version": REVIEW_SCHEMA_VERSION,
            "story_rel_path": story_rel_path,
            "story_id": story_id,
            "stage": stage_name,
            "updated_at": _utc_now_iso(),
            "decisions": [
                {
                    "finding_id": str(item.get("id", "")),
                    "decision": _normalize_choice_decision(str(item.get("decision", "pending"))),
                    "selected_option": str(item.get("selected_option", "")).strip().upper(),
                    "notes": str(item.get("notes", "")),
                }
                for item in findings
            ],
        },
    )


def _run_stage_cycle_pass(
    *,
    book_rel_path: str,
    story_id: str,
    stage: str,
    severity_band: str,
    pass_index: int,
    context_payload: dict[str, Any],
    canonical_story_pdf_rel: str,
    auto_decide: bool,
    apply_decisions: bool = True,
) -> dict[str, Any]:
    story_rel_path = f"{_normalize_rel_path(book_rel_path)}/{story_id}"
    story_payload = load_story(story_rel_path)

    all_findings = _findings_for_stage(
        stage=stage,
        story_payload=story_payload,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
        context_payload=context_payload,
    )
    findings = _filter_findings_by_severity(all_findings, severity_band=severity_band)
    choices_map = _sync_choices_file(
        book_rel_path=book_rel_path,
        story_id=story_id,
        stage=stage,
        severity_band=severity_band,
        pass_index=pass_index,
        findings=findings,
        auto_decide=auto_decide,
    )
    _merge_choices_into_findings(findings, choices_map)

    changed = False
    if apply_decisions:
        changed = _apply_selected_suggestions(story_payload=story_payload, findings=findings)
        if changed:
            save_story_payload(story_rel_path=story_rel_path, payload=story_payload, touch_updated_at=True)
            story_payload = load_story(story_rel_path)
            all_findings = _findings_for_stage(
                stage=stage,
                story_payload=story_payload,
                canonical_story_pdf_rel=canonical_story_pdf_rel,
                context_payload=context_payload,
            )
            findings = _filter_findings_by_severity(all_findings, severity_band=severity_band)
            _merge_choices_into_findings(findings, choices_map)

    open_findings = sum(1 for item in findings if _finding_is_open(item, severity_band))
    contrast_alerts = _contrast_alerts_for_stage(
        stage=stage,
        severity_band=severity_band,
        story_payload=story_payload,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
    )
    open_contrast = sum(1 for item in contrast_alerts if str(item.get("status", "open")) == "open")
    alerts_open = open_findings + open_contrast

    paths = _review_paths(book_rel_path, story_id)
    _write_json(
        paths["findings_json"],
        {
            "schema_version": CASCADE_SCHEMA_VERSION,
            "story_rel_path": story_rel_path,
            "story_id": story_id,
            "stage": stage,
            "severity_band": severity_band,
            "pass_index": int(pass_index),
            "generated_at": _utc_now_iso(),
            "findings": findings,
        },
    )
    _write_json(
        paths["contrast_json"],
        {
            "schema_version": CASCADE_SCHEMA_VERSION,
            "story_rel_path": story_rel_path,
            "story_id": story_id,
            "stage": stage,
            "severity_band": severity_band,
            "pass_index": int(pass_index),
            "generated_at": _utc_now_iso(),
            "alerts": contrast_alerts,
            "alerts_open": int(open_contrast),
            "status": "alert" if open_contrast > 0 else "ok",
        },
    )
    _write_legacy_sidecars(
        book_rel_path=book_rel_path,
        story_id=story_id,
        story_rel_path=story_rel_path,
        stage=stage,
        findings=findings,
        severity_band=severity_band,
        pass_index=pass_index,
    )
    return {
        "story_id": story_id,
        "story_rel_path": story_rel_path,
        "stage": stage,
        "severity_band": severity_band,
        "pass_index": int(pass_index),
        "findings": len(findings),
        "open_findings": int(open_findings),
        "open_contrast": int(open_contrast),
        "alerts_open": int(alerts_open),
        "applied_changes": bool(changed),
        "findings_json_rel": _to_project_rel(paths["findings_json"]),
        "choices_json_rel": _to_project_rel(paths["choices_json"]),
        "contrast_json_rel": _to_project_rel(paths["contrast_json"]),
    }


def _update_pipeline_progress(
    *,
    state: dict[str, Any],
    book_rel_path: str,
    stage: str,
    severity_band: str,
    pass_index: int,
    convergence_status: str,
    alerts_open: dict[str, int],
) -> None:
    normalized_alerts = {severity: 0 for severity in SEVERITY_ORDER}
    for key, value in alerts_open.items():
        if key in normalized_alerts:
            normalized_alerts[key] = int(value)

    state["stage"] = stage
    state["severity_band"] = severity_band
    state["pass_index"] = int(pass_index)
    state["convergence_status"] = convergence_status
    state["alerts_open"] = normalized_alerts
    state["generated_at"] = _utc_now_iso()
    _write_pipeline_state(book_rel_path, state)


def _run_stage_cascade_for_story(
    *,
    book_rel_path: str,
    story_id: str,
    stage: str,
    context_payload: dict[str, Any],
    canonical_story_pdf_rel: str,
    state: dict[str, Any],
    auto_decide: bool,
) -> dict[str, Any]:
    story_rel_path = f"{_normalize_rel_path(book_rel_path)}/{story_id}"
    stage_rows: dict[str, Any] = {"stage": stage, "severities": {}, "status": "in_progress"}

    for severity in SEVERITY_ORDER:
        max_passes = int(MAX_PASSES_BY_SEVERITY[severity])
        converged = False
        last_summary: dict[str, Any] | None = None
        for pass_index in range(1, max_passes + 1):
            summary = _run_stage_cycle_pass(
                book_rel_path=book_rel_path,
                story_id=story_id,
                stage=stage,
                severity_band=severity,
                pass_index=pass_index,
                context_payload=context_payload,
                canonical_story_pdf_rel=canonical_story_pdf_rel,
                auto_decide=auto_decide,
            )
            last_summary = summary
            converged = summary["alerts_open"] == 0
            _append_pass_record(
                book_rel_path=book_rel_path,
                story_id=story_id,
                story_rel_path=story_rel_path,
                stage=stage,
                severity_band=severity,
                pass_index=pass_index,
                findings_count=summary["findings"],
                alerts_open=summary["alerts_open"],
                applied_changes=summary["applied_changes"],
                converged=converged,
                max_passes_reached=bool((not converged) and pass_index == max_passes),
            )
            _update_pipeline_progress(
                state=state,
                book_rel_path=book_rel_path,
                stage=stage,
                severity_band=severity,
                pass_index=pass_index,
                convergence_status=(
                    "converged"
                    if converged
                    else "max_passes_reached"
                    if pass_index == max_passes
                    else "in_progress"
                ),
                alerts_open={severity: int(summary["alerts_open"])},
            )
            if converged:
                break

        stage_rows["severities"][severity] = {
            "converged": converged,
            "passes": int(last_summary["pass_index"]) if last_summary else 0,
            "alerts_open": int(last_summary["alerts_open"]) if last_summary else 0,
            "max_passes": max_passes,
        }
        if (not converged) and severity in BLOCKING_SEVERITIES:
            stage_rows["status"] = "blocked"
            stage_rows["blocked_severity"] = severity
            stage_rows["reason"] = f"{stage}_blocked"
            _update_pipeline_progress(
                state=state,
                book_rel_path=book_rel_path,
                stage=stage,
                severity_band=severity,
                pass_index=max_passes,
                convergence_status="max_passes_reached",
                alerts_open={severity: int(stage_rows["severities"][severity]["alerts_open"])},
            )
            return stage_rows

    stage_rows["status"] = "reviewed"
    return stage_rows


def run_text_detection(
    *,
    inbox_book_title: str,
    book_rel_path: str,
    story_id: str,
    severity_band: str,
    pass_index: int = 1,
) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book, _ = _validate_story_exists(book_rel_path, story_id)
    story_id = _validate_story_id(story_id)
    severity_band = _validate_severity_band(severity_band)
    pass_index = _validate_pass_index(pass_index)

    context = run_contexto_canon(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    canonical_story_pdf_rel = str(context.get("canonical_pdfs", {}).get("story_pdf_by_id", {}).get(story_id, ""))
    return _run_stage_cycle_pass(
        book_rel_path=normalized_book,
        story_id=story_id,
        stage=STAGE_TEXT,
        severity_band=severity_band,
        pass_index=pass_index,
        context_payload=context,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
        auto_decide=False,
        apply_decisions=False,
    )


def run_text_decision_interactiva(
    *,
    inbox_book_title: str,
    book_rel_path: str,
    story_id: str,
    severity_band: str,
    pass_index: int = 1,
) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book, _ = _validate_story_exists(book_rel_path, story_id)
    story_id = _validate_story_id(story_id)
    severity_band = _validate_severity_band(severity_band)
    pass_index = _validate_pass_index(pass_index)

    context = run_contexto_canon(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    canonical_story_pdf_rel = str(context.get("canonical_pdfs", {}).get("story_pdf_by_id", {}).get(story_id, ""))
    return _run_stage_cycle_pass(
        book_rel_path=normalized_book,
        story_id=story_id,
        stage=STAGE_TEXT,
        severity_band=severity_band,
        pass_index=pass_index,
        context_payload=context,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
        auto_decide=False,
        apply_decisions=True,
    )


def run_text_contrast_canon(
    *,
    inbox_book_title: str,
    book_rel_path: str,
    story_id: str,
    severity_band: str,
) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book, story_rel_path = _validate_story_exists(book_rel_path, story_id)
    story_id = _validate_story_id(story_id)
    severity_band = _validate_severity_band(severity_band)

    context = run_contexto_canon(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    story_payload = load_story(story_rel_path)
    canonical_story_pdf_rel = str(context.get("canonical_pdfs", {}).get("story_pdf_by_id", {}).get(story_id, ""))
    alerts = _contrast_alerts_for_stage(
        stage=STAGE_TEXT,
        severity_band=severity_band,
        story_payload=story_payload,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
    )
    paths = _review_paths(normalized_book, story_id)
    _write_json(
        paths["contrast_json"],
        {
            "schema_version": CASCADE_SCHEMA_VERSION,
            "story_rel_path": story_rel_path,
            "story_id": story_id,
            "stage": STAGE_TEXT,
            "severity_band": severity_band,
            "pass_index": 0,
            "generated_at": _utc_now_iso(),
            "alerts": alerts,
            "alerts_open": sum(1 for item in alerts if str(item.get("status", "open")) == "open"),
            "status": "alert" if alerts else "ok",
        },
    )
    return {
        "story_id": story_id,
        "story_rel_path": story_rel_path,
        "alerts": len(alerts),
        "contrast_json_rel": _to_project_rel(paths["contrast_json"]),
    }


def run_prompt_detection(
    *,
    inbox_book_title: str,
    book_rel_path: str,
    story_id: str,
    severity_band: str,
    pass_index: int = 1,
) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book, _ = _validate_story_exists(book_rel_path, story_id)
    story_id = _validate_story_id(story_id)
    severity_band = _validate_severity_band(severity_band)
    pass_index = _validate_pass_index(pass_index)

    context = run_contexto_canon(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    canonical_story_pdf_rel = str(context.get("canonical_pdfs", {}).get("story_pdf_by_id", {}).get(story_id, ""))
    return _run_stage_cycle_pass(
        book_rel_path=normalized_book,
        story_id=story_id,
        stage=STAGE_PROMPT,
        severity_band=severity_band,
        pass_index=pass_index,
        context_payload=context,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
        auto_decide=False,
        apply_decisions=False,
    )


def run_prompt_decision_interactiva(
    *,
    inbox_book_title: str,
    book_rel_path: str,
    story_id: str,
    severity_band: str,
    pass_index: int = 1,
) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book, _ = _validate_story_exists(book_rel_path, story_id)
    story_id = _validate_story_id(story_id)
    severity_band = _validate_severity_band(severity_band)
    pass_index = _validate_pass_index(pass_index)

    context = run_contexto_canon(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    canonical_story_pdf_rel = str(context.get("canonical_pdfs", {}).get("story_pdf_by_id", {}).get(story_id, ""))
    return _run_stage_cycle_pass(
        book_rel_path=normalized_book,
        story_id=story_id,
        stage=STAGE_PROMPT,
        severity_band=severity_band,
        pass_index=pass_index,
        context_payload=context,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
        auto_decide=False,
        apply_decisions=True,
    )


def run_prompt_contrast_canon(
    *,
    inbox_book_title: str,
    book_rel_path: str,
    story_id: str,
    severity_band: str,
) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book, story_rel_path = _validate_story_exists(book_rel_path, story_id)
    story_id = _validate_story_id(story_id)
    severity_band = _validate_severity_band(severity_band)

    context = run_contexto_canon(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    story_payload = load_story(story_rel_path)
    canonical_story_pdf_rel = str(context.get("canonical_pdfs", {}).get("story_pdf_by_id", {}).get(story_id, ""))
    alerts = _contrast_alerts_for_stage(
        stage=STAGE_PROMPT,
        severity_band=severity_band,
        story_payload=story_payload,
        canonical_story_pdf_rel=canonical_story_pdf_rel,
    )
    paths = _review_paths(normalized_book, story_id)
    _write_json(
        paths["contrast_json"],
        {
            "schema_version": CASCADE_SCHEMA_VERSION,
            "story_rel_path": story_rel_path,
            "story_id": story_id,
            "stage": STAGE_PROMPT,
            "severity_band": severity_band,
            "pass_index": 0,
            "generated_at": _utc_now_iso(),
            "alerts": alerts,
            "alerts_open": sum(1 for item in alerts if str(item.get("status", "open")) == "open"),
            "status": "alert" if alerts else "ok",
        },
    )
    return {
        "story_id": story_id,
        "story_rel_path": story_rel_path,
        "alerts": len(alerts),
        "contrast_json_rel": _to_project_rel(paths["contrast_json"]),
    }


def run_orquestador_editorial(*, inbox_book_title: str, book_rel_path: str) -> dict[str, Any]:
    inbox_book_title = _validate_inbox_book_title(inbox_book_title)
    normalized_book = _validate_book_rel_path(book_rel_path)
    context_payload = run_contexto_canon(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    state = run_ingesta_json(inbox_book_title=inbox_book_title, book_rel_path=normalized_book)
    stories = state.get("stories", [])
    canonical_pdf_map = context_payload.get("canonical_pdfs", {}).get("story_pdf_by_id", {})

    blocked_story: dict[str, Any] | None = None
    totals = _empty_metrics()

    state["phase"] = "cascade_text"
    state["stage"] = STAGE_TEXT
    state["severity_band"] = "critical"
    state["pass_index"] = 0
    state["convergence_status"] = "in_progress"
    state["alerts_open"] = {key: 0 for key in SEVERITY_ORDER}
    state["context_chain_rel"] = context_payload.get("context_chain_rel", "")
    state["glossary_merged_rel"] = context_payload.get("glossary_merged_rel", "")
    _write_pipeline_state(normalized_book, state)

    for row in stories:
        story_id = str(row.get("story_id", ""))
        canonical_story_pdf_rel = str(canonical_pdf_map.get(story_id, ""))

        text_summary = _run_stage_cascade_for_story(
            book_rel_path=normalized_book,
            story_id=story_id,
            stage=STAGE_TEXT,
            context_payload=context_payload,
            canonical_story_pdf_rel=canonical_story_pdf_rel,
            state=state,
            auto_decide=True,
        )
        row["text_stage"] = text_summary
        for severity in SEVERITY_ORDER:
            totals[f"{severity}_open"] += int(text_summary["severities"].get(severity, {}).get("alerts_open", 0))
        if text_summary["status"] == "blocked":
            set_story_status(story_rel_path=row["story_rel_path"], status="text_blocked")
            blocked_story = {
                "story_id": story_id,
                "story_rel_path": row["story_rel_path"],
                "reason": "text_blocked",
                "severity_band": str(text_summary.get("blocked_severity", "")),
            }
            break
        set_story_status(story_rel_path=row["story_rel_path"], status="text_reviewed")

        state["phase"] = "cascade_prompt"
        state["stage"] = STAGE_PROMPT
        _write_pipeline_state(normalized_book, state)
        prompt_summary = _run_stage_cascade_for_story(
            book_rel_path=normalized_book,
            story_id=story_id,
            stage=STAGE_PROMPT,
            context_payload=context_payload,
            canonical_story_pdf_rel=canonical_story_pdf_rel,
            state=state,
            auto_decide=True,
        )
        row["prompt_stage"] = prompt_summary
        for severity in SEVERITY_ORDER:
            totals[f"{severity}_open"] += int(prompt_summary["severities"].get(severity, {}).get("alerts_open", 0))
        if prompt_summary["status"] == "blocked":
            set_story_status(story_rel_path=row["story_rel_path"], status="prompt_blocked")
            blocked_story = {
                "story_id": story_id,
                "story_rel_path": row["story_rel_path"],
                "reason": "prompt_blocked",
                "severity_band": str(prompt_summary.get("blocked_severity", "")),
            }
            break

        set_story_status(story_rel_path=row["story_rel_path"], status="ready")
        row["status"] = "ready"

    state["generated_at"] = _utc_now_iso()
    state["totals"].update(totals)
    if blocked_story:
        state["phase"] = "blocked"
        state["blocked_story"] = blocked_story
    else:
        state["phase"] = "completed"
        state["blocked_story"] = None
        state["convergence_status"] = "converged"
    pipeline_state_path = _write_pipeline_state(normalized_book, state)
    state["pipeline_state_rel"] = _to_project_rel(pipeline_state_path)
    return state
