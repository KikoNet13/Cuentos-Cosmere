from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "library").exists():
            return candidate
    return Path.cwd().resolve()


REPO_ROOT = _repo_root(Path(__file__).resolve())
ORQUESTADOR_SCRIPTS = REPO_ROOT / ".codex" / "skills" / "adaptacion-orquestador" / "scripts"
if str(ORQUESTADOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ORQUESTADOR_SCRIPTS))

from adaptacion_lib import (  # noqa: E402
    SEVERITIES,
    append_jsonl,
    build_finding_id,
    decisions_log_path_for_story,
    ensure_review_contract,
    load_json,
    next_option_letter,
    parse_apply_decisions,
    resolve_option_value,
    review_path_for_story,
    save_json,
    save_review,
    story_json_path,
    story_rel_path_no_ext,
    update_story_status,
    upsert_open_findings,
    utc_now_iso,
)


def _word_count(value: str) -> int:
    return len([token for token in value.split() if token.strip()])


def _prompt_from_text(text_value: str) -> str:
    snippet = " ".join(text_value.split())[:180].strip()
    if not snippet:
        snippet = "Escena narrativa principal del cuento."
    return (
        f"ESCENA: {snippet}\n"
        "ESTILO: Ilustracion narrativa infantil coherente con Cosmere.\n"
        "COMPOSICION: Plano medio con foco claro en los personajes principales.\n"
        "RESTRICCIONES: Sin texto incrustado, sin marcas de agua, anatomia consistente."
    )


def _build_proposals(
    *,
    issue_type: str,
    prompt_current: str,
    prompt_original: str,
    page_text_current: str,
) -> list[dict[str, str]]:
    candidates: list[str] = []
    if issue_type == "missing_prompt_main":
        if prompt_original.strip():
            candidates.append(prompt_original.strip())
        candidates.append(_prompt_from_text(page_text_current))
    elif issue_type == "short_prompt_main":
        if prompt_original.strip():
            candidates.append(prompt_original.strip())
        candidates.append(_prompt_from_text(page_text_current))
        candidates.append(
            (
                f"{prompt_current.strip()}\n"
                "ESTILO: Ilustracion narrativa infantil clara.\n"
                "RESTRICCIONES: Sin texto incrustado ni marcas de agua."
            ).strip()
        )
    elif issue_type == "placeholder_marker":
        cleaned = re.sub(r"\b(TODO|FIXME)\b", "", prompt_current, flags=re.IGNORECASE).strip()
        candidates.append(cleaned or prompt_original.strip() or _prompt_from_text(page_text_current))
    elif issue_type == "draft_marker":
        cleaned = prompt_current.replace("[[", "").replace("]]", "").strip()
        candidates.append(cleaned or prompt_original.strip() or _prompt_from_text(page_text_current))
    else:
        candidates.append(prompt_current.strip() or prompt_original.strip() or _prompt_from_text(page_text_current))

    normalized: list[str] = []
    for candidate in candidates:
        value = candidate.strip()
        if value and value not in normalized:
            normalized.append(value)

    proposals: list[dict[str, str]] = []
    for index, value in enumerate(normalized[:3]):
        proposals.append(
            {
                "option": next_option_letter(index),
                "label": "Propuesta IA",
                "value": value,
            }
        )
    return proposals


def _build_finding(
    *,
    severity: str,
    page_number: int,
    issue_type: str,
    message: str,
    prompt_current: str,
    prompt_original: str,
    page_text_current: str,
) -> dict[str, Any]:
    finding_id = build_finding_id(
        stage="prompts",
        severity=severity,
        page_number=page_number,
        issue_type=issue_type,
        content=prompt_current or prompt_original or page_text_current,
    )
    return {
        "finding_id": finding_id,
        "stage": "prompts",
        "severity": severity,
        "page_number": page_number,
        "slot_name": "main",
        "issue_type": issue_type,
        "message": message,
        "status": "open",
        "created_at": utc_now_iso(),
        "proposals": _build_proposals(
            issue_type=issue_type,
            prompt_current=prompt_current,
            prompt_original=prompt_original,
            page_text_current=page_text_current,
        ),
    }


def detect_prompt_findings(story: dict[str, Any], severity: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for page in story.get("pages", []):
        page_number = int(page.get("page_number", 0))
        text_obj = page.get("text", {})
        page_text_current = str(text_obj.get("current", "") or "")

        main_slot = ((page.get("images") or {}).get("main") or {})
        prompt_obj = main_slot.get("prompt") or {}
        prompt_current = str(prompt_obj.get("current", "") or "")
        prompt_original = str(prompt_obj.get("original", "") or "")
        normalized = prompt_current.strip()

        if severity == "critical":
            if not normalized:
                findings.append(
                    _build_finding(
                        severity=severity,
                        page_number=page_number,
                        issue_type="missing_prompt_main",
                        message="El slot visual obligatorio prompt.main no tiene contenido actual.",
                        prompt_current=prompt_current,
                        prompt_original=prompt_original,
                        page_text_current=page_text_current,
                    )
                )
        elif severity == "major":
            if normalized and _word_count(normalized) < 8:
                findings.append(
                    _build_finding(
                        severity=severity,
                        page_number=page_number,
                        issue_type="short_prompt_main",
                        message="prompt.main es demasiado corto para guiar la ilustracion.",
                        prompt_current=prompt_current,
                        prompt_original=prompt_original,
                        page_text_current=page_text_current,
                    )
                )
        elif severity == "minor":
            if re.search(r"\b(TODO|FIXME)\b", normalized, flags=re.IGNORECASE):
                findings.append(
                    _build_finding(
                        severity=severity,
                        page_number=page_number,
                        issue_type="placeholder_marker",
                        message="prompt.main contiene marcadores pendientes (TODO/FIXME).",
                        prompt_current=prompt_current,
                        prompt_original=prompt_original,
                        page_text_current=page_text_current,
                    )
                )
        elif severity == "info":
            if "[[" in normalized and "]]" in normalized:
                findings.append(
                    _build_finding(
                        severity=severity,
                        page_number=page_number,
                        issue_type="draft_marker",
                        message="prompt.main contiene marcas de borrador [[...]].",
                        prompt_current=prompt_current,
                        prompt_original=prompt_original,
                        page_text_current=page_text_current,
                    )
                )
    return findings


def apply_decisions(
    *,
    story: dict[str, Any],
    review: dict[str, Any],
    decisions: list[dict[str, Any]],
    story_path: Path,
) -> list[dict[str, Any]]:
    if not decisions:
        return []
    by_finding = {finding.get("finding_id"): finding for finding in review.get("findings", [])}
    pages = {int(page.get("page_number", 0)): page for page in story.get("pages", [])}
    applied: list[dict[str, Any]] = []
    decisions_log_path = decisions_log_path_for_story(story_path)

    for decision in decisions:
        finding_id = str(decision.get("finding_id", "")).strip()
        if not finding_id:
            raise ValueError("Cada decision requiere finding_id")
        finding = by_finding.get(finding_id)
        if not finding or finding.get("stage") != "prompts":
            raise ValueError(f"finding_id no valido para prompts: {finding_id}")
        if finding.get("status") != "open":
            continue

        page_number = int(finding.get("page_number", 0))
        page = pages.get(page_number)
        if page is None:
            raise ValueError(f"Pagina inexistente para finding {finding_id}: {page_number}")
        main_slot = ((page.get("images") or {}).get("main") or {})
        prompt_obj = main_slot.setdefault("prompt", {})

        selected_option = str(decision.get("selected_option", "A")).strip().upper()
        custom_prompt = decision.get("custom_prompt_main")
        if custom_prompt is None:
            custom_prompt = decision.get("final_prompt_main")

        final_prompt = resolve_option_value(
            finding,
            selected_option=selected_option,
            custom_value=str(custom_prompt) if custom_prompt is not None else None,
        )

        prompt_obj["current"] = final_prompt
        finding["status"] = "resolved"
        finding["resolved_at"] = utc_now_iso()
        finding["resolved_by"] = str(decision.get("resolved_by", "human"))
        finding["selected_option"] = selected_option

        log_row = {
            "finding_id": finding_id,
            "stage": "prompts",
            "severity": finding.get("severity"),
            "decision": "resolved",
            "selected_option": selected_option,
            "final_prompt_main": final_prompt,
            "resolved_by": finding["resolved_by"],
            "resolved_at": finding["resolved_at"],
        }
        review.setdefault("decisions", []).append(log_row)
        append_jsonl(decisions_log_path, log_row)
        applied.append(log_row)

    review.setdefault("metrics", {}).setdefault("decisions_applied_total", 0)
    review["metrics"]["decisions_applied_total"] = int(review["metrics"]["decisions_applied_total"]) + len(applied)
    return applied


def run(story_rel_path: str, severity: str, target_age: int | None, apply_decision_json: str | None) -> dict[str, Any]:
    story_path = story_json_path(story_rel_path)
    story = load_json(story_path)
    update_story_status(story, "in_review")

    review = ensure_review_contract(
        story_path,
        target_age=target_age,
        phase="prompts",
        severity_cursor=severity,
    )
    review["status"] = "in_review"
    review["target_age"] = target_age if target_age is not None else review.get("target_age")

    findings = detect_prompt_findings(story, severity)
    upsert_open_findings(review, stage="prompts", severity=severity, findings=findings)
    review.setdefault("metrics", {}).setdefault("runs", {}).setdefault("prompts", 0)
    review["metrics"]["runs"]["prompts"] = int(review["metrics"]["runs"]["prompts"]) + 1

    decisions = parse_apply_decisions(apply_decision_json)
    applied = apply_decisions(story=story, review=review, decisions=decisions, story_path=story_path)

    save_json(story_path, story)
    review_path = save_review(story_path, review)

    return {
        "ok": True,
        "story_rel_path": story_rel_path_no_ext(story_path),
        "severity": severity,
        "findings": findings,
        "applied": {
            "count": len(applied),
            "items": applied,
        },
        "open_counts": review.get("open_counts", {}),
        "review_rel_path": review_path.relative_to(REPO_ROOT).as_posix(),
        "review_file": review_path_for_story(story_path).relative_to(REPO_ROOT).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detectar y aplicar decisiones de adaptacion de prompt.main.")
    parser.add_argument("--story-rel-path", required=True, help="Ruta relativa del cuento, con o sin .json.")
    parser.add_argument("--severity", required=True, choices=SEVERITIES, help="Banda de severidad.")
    parser.add_argument("--target-age", type=int, default=None, help="Edad objetivo activa.")
    parser.add_argument(
        "--apply-decision-json",
        default=None,
        help="JSON inline, objeto/lista, o ruta a archivo con decisiones para aplicar.",
    )
    args = parser.parse_args()

    try:
        result = run(
            story_rel_path=args.story_rel_path,
            severity=args.severity,
            target_age=args.target_age,
            apply_decision_json=args.apply_decision_json,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

