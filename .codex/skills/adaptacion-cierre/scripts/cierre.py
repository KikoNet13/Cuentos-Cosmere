from __future__ import annotations

import argparse
import json
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
    build_finding_id,
    ensure_review_contract,
    load_json,
    recompute_open_counts,
    save_json,
    save_review,
    story_json_path,
    story_rel_path_no_ext,
    update_story_status,
    utc_now_iso,
)


def _inject_blockers(story: dict[str, Any], review: dict[str, Any]) -> list[dict[str, Any]]:
    existing_open_ids = {
        finding.get("finding_id")
        for finding in review.get("findings", [])
        if finding.get("status") == "open"
    }
    injected: list[dict[str, Any]] = []

    for page in story.get("pages", []):
        page_number = int(page.get("page_number", 0))
        text_current = str((page.get("text") or {}).get("current", "") or "").strip()
        if not text_current:
            finding_id = build_finding_id(
                stage="text",
                severity="critical",
                page_number=page_number,
                issue_type="empty_text",
                content="",
            )
            if finding_id not in existing_open_ids:
                injected.append(
                    {
                        "finding_id": finding_id,
                        "stage": "text",
                        "severity": "critical",
                        "page_number": page_number,
                        "issue_type": "empty_text",
                        "message": "La pagina no tiene texto actual.",
                        "status": "open",
                        "created_at": utc_now_iso(),
                        "proposals": [],
                    }
                )
                existing_open_ids.add(finding_id)

        main_prompt = str((((page.get("images") or {}).get("main") or {}).get("prompt") or {}).get("current", "") or "").strip()
        if not main_prompt:
            finding_id = build_finding_id(
                stage="prompts",
                severity="critical",
                page_number=page_number,
                issue_type="missing_prompt_main",
                content="",
            )
            if finding_id not in existing_open_ids:
                injected.append(
                    {
                        "finding_id": finding_id,
                        "stage": "prompts",
                        "severity": "critical",
                        "page_number": page_number,
                        "slot_name": "main",
                        "issue_type": "missing_prompt_main",
                        "message": "El slot visual obligatorio prompt.main no tiene contenido actual.",
                        "status": "open",
                        "created_at": utc_now_iso(),
                        "proposals": [],
                    }
                )
                existing_open_ids.add(finding_id)

    if injected:
        review.setdefault("findings", []).extend(injected)
    return injected


def run(story_rel_path: str) -> dict[str, Any]:
    story_path = story_json_path(story_rel_path)
    story = load_json(story_path)
    review = ensure_review_contract(story_path, phase="cierre", severity_cursor=None)

    review.setdefault("metrics", {}).setdefault("runs", {}).setdefault("cierre", 0)
    review["metrics"]["runs"]["cierre"] = int(review["metrics"]["runs"]["cierre"]) + 1

    injected = _inject_blockers(story, review)
    open_counts = recompute_open_counts(review)
    total_open = sum(open_counts.values())

    if total_open == 0:
        review["status"] = "definitive"
        review["phase"] = "done"
        update_story_status(story, "definitive")
        for page in story.get("pages", []):
            page["status"] = "definitive"
            main = ((page.get("images") or {}).get("main") or {})
            if main:
                main["status"] = "definitive"
    else:
        review["status"] = "in_review"
        review["phase"] = "cierre"
        update_story_status(story, "in_review")

    save_json(story_path, story)
    review_path = save_review(story_path, review)

    return {
        "ok": True,
        "story_rel_path": story_rel_path_no_ext(story_path),
        "status": story.get("status"),
        "phase": review.get("phase"),
        "open_counts": open_counts,
        "blockers_injected": injected,
        "review_rel_path": review_path.relative_to(REPO_ROOT).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar cierre editorial y cambiar estado a definitive si procede.")
    parser.add_argument("--story-rel-path", required=True, help="Ruta relativa del cuento, con o sin .json.")
    args = parser.parse_args()

    try:
        result = run(story_rel_path=args.story_rel_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

