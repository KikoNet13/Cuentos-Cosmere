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
REVIEW_SCHEMA_VERSION = "1.0"
PIPELINE_SCHEMA_VERSION = "1.0"

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


class EditorialOsmosisError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


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
        "pipeline_state_json": reviews_dir / "pipeline_state.json",
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
    return any(token in text for token in ("Ã", "Â", "�"))


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
        r"^\s*##\s*P(?:a|á|Ã¡)?.*?(\d+)\s*(?:</h2>)?\s*$",
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
        rf"{re.escape(label)}\s*:\s*```(?:text)?\s*\r?\n(.*?)\r?\n```",
        flags=re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(section)
    if match:
        return match.group(1).strip()
    fallback_pattern = re.compile(
        rf"{re.escape(label)}\s*:\s*(.*)",
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
        raise EditorialOsmosisError(
            f"No se detectaron paginas en {md_path}. Se esperaba '## Pagina NN'."
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
    inbox_root = (LIBRARY_ROOT / "_inbox" / inbox_book_title).resolve()
    if not inbox_root.exists() or not inbox_root.is_dir():
        raise EditorialOsmosisError(f"No existe el libro en inbox: {inbox_root}")

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
        "book_rel_path": _normalize_rel_path(book_rel_path),
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
        "pipeline": "editorial_osmosis",
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
    subject = _short_sentence(page_text, "Personaje principal de la pagina.")
    scene = _short_sentence(base_prompt, "Escena clave del cuento con foco narrativo.")
    continuity = _short_sentence(page_text, "Mantener continuidad con las paginas vecinas.")
    return "\n".join(
        [
            f"SUJETO: {subject}",
            f"ESCENA: {scene}",
            "ESTILO: Ilustracion narrativa infantil coherente con Cosmere.",
            "COMPOSICION: Plano medio, lectura clara y foco en accion principal.",
            "ILUMINACION_COLOR: Paleta ceniza rojiza con contraste suave.",
            f"CONTINUIDAD: {continuity}",
            "RESTRICCIONES: Sin texto incrustado, sin marcas de agua, anatomia consistente.",
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
                    "label": "Mantener vacio",
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
                    evidence="La pagina no tiene texto actual.",
                    suggestions=suggestions,
                )
            )
            continue

        if _contains_mojibake(text_current):
            repaired = _try_fix_mojibake(text_current)
            suggestions = [
                {
                    "id": "A",
                    "label": "Aplicar reparacion de codificacion",
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
                    evidence="Se detectaron espacios dobles o multiples.",
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
                    "label": "Mantener vacio",
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
                    evidence="El prompt main actual esta vacio.",
                    suggestions=suggestions,
                )
            )
            continue

        if _contains_mojibake(main_prompt):
            repaired = _try_fix_mojibake(main_prompt)
            suggestions = [
                {
                    "id": "A",
                    "label": "Aplicar reparacion de codificacion",
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
            f"  decision: {finding.get('decision', 'pending')} | opcion: {finding.get('selected_option', '') or '-'}"
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
        raise EditorialOsmosisError(f"Etapa no soportada: {stage}")

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


def run_osmosis_pipeline(*, inbox_book_title: str, book_rel_path: str) -> dict[str, Any]:
    state = run_ingesta_json(inbox_book_title=inbox_book_title, book_rel_path=book_rel_path)
    stories = state.get("stories", [])

    state["phase"] = "text_stage"
    _write_pipeline_state(book_rel_path, state)

    blocked_story: dict[str, Any] | None = None
    total_metrics = _empty_metrics()

    for row in stories:
        story_id = row["story_id"]
        text_audit_summary = run_text_audit(book_rel_path=book_rel_path, story_id=story_id)
        text_correction_summary = run_text_correction(book_rel_path=book_rel_path, story_id=story_id)
        row["text_stage"] = {
            "audit": text_audit_summary,
            "correction": text_correction_summary,
        }

        total_metrics["critical_open"] += int(text_correction_summary["metrics"]["critical_open"])
        total_metrics["major_open"] += int(text_correction_summary["metrics"]["major_open"])
        total_metrics["minor_open"] += int(text_correction_summary["metrics"]["minor_open"])
        total_metrics["info_open"] += int(text_correction_summary["metrics"]["info_open"])

        if text_correction_summary["status"] == "blocked":
            blocked_story = {
                "story_id": story_id,
                "story_rel_path": row["story_rel_path"],
                "reason": "text_blocked",
            }
            break

        prompt_audit_summary = run_prompt_audit(book_rel_path=book_rel_path, story_id=story_id)
        prompt_correction_summary = run_prompt_correction(book_rel_path=book_rel_path, story_id=story_id)
        row["prompt_stage"] = {
            "audit": prompt_audit_summary,
            "correction": prompt_correction_summary,
        }

        total_metrics["critical_open"] += int(prompt_correction_summary["metrics"]["critical_open"])
        total_metrics["major_open"] += int(prompt_correction_summary["metrics"]["major_open"])
        total_metrics["minor_open"] += int(prompt_correction_summary["metrics"]["minor_open"])
        total_metrics["info_open"] += int(prompt_correction_summary["metrics"]["info_open"])

        if prompt_correction_summary["status"] == "blocked":
            blocked_story = {
                "story_id": story_id,
                "story_rel_path": row["story_rel_path"],
                "reason": "prompt_blocked",
            }
            break

        set_story_status(story_rel_path=row["story_rel_path"], status="ready")
        row["status"] = "ready"

    if blocked_story:
        state["phase"] = "blocked"
        state["blocked_story"] = blocked_story
    else:
        state["phase"] = "completed"
        state["blocked_story"] = None

    state["generated_at"] = _utc_now_iso()
    state["totals"].update(total_metrics)
    pipeline_state_path = _write_pipeline_state(book_rel_path, state)
    state["pipeline_state_rel"] = _to_project_rel(pipeline_state_path)
    return state
