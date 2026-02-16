from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from adaptacion_lib import REPO_ROOT, ensure_story_from_markdown, story_rel_path_no_ext

SEVERITY_ORDER = ("critical", "major", "minor", "info")

CONTEXTO_SCRIPT = REPO_ROOT / ".codex" / "skills" / "adaptacion-contexto" / "scripts" / "contexto.py"
TEXTO_SCRIPT = REPO_ROOT / ".codex" / "skills" / "adaptacion-texto" / "scripts" / "texto.py"
PROMPTS_SCRIPT = REPO_ROOT / ".codex" / "skills" / "adaptacion-prompts" / "scripts" / "prompts.py"
CIERRE_SCRIPT = REPO_ROOT / ".codex" / "skills" / "adaptacion-cierre" / "scripts" / "cierre.py"


def _run_json_script(script_path: Path, args: list[str]) -> dict[str, Any]:
    cmd = [sys.executable, str(script_path), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    if proc.returncode != 0:
        raise RuntimeError(f"Fallo {script_path.name}: {stdout or stderr}")
    if not stdout:
        raise RuntimeError(f"Salida vacia de {script_path.name}")
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON invalido en {script_path.name}: {stdout}") from exc
    if not data.get("ok", False):
        raise RuntimeError(f"Error reportado por {script_path.name}: {data.get('error')}")
    return data


def run(inbox_book_title: str, book_rel_path: str, target_age: int) -> dict[str, Any]:
    contexto = _run_json_script(
        CONTEXTO_SCRIPT,
        [
            "--inbox-book-title",
            inbox_book_title,
            "--book-rel-path",
            book_rel_path,
            "--target-age",
            str(target_age),
        ],
    )
    stories_inventory = contexto.get("inventory", {}).get("stories", [])
    if not stories_inventory:
        raise RuntimeError("No se encontraron propuestas NN.md en inbox para orquestar")

    stories_summary: list[dict[str, Any]] = []
    for story_row in stories_inventory:
        md_rel_path = story_row.get("markdown_rel_path")
        if not md_rel_path:
            continue
        markdown_abs = REPO_ROOT / md_rel_path
        story_path = ensure_story_from_markdown(book_rel_path, markdown_abs)
        story_rel = story_rel_path_no_ext(story_path)

        text_by_severity: dict[str, Any] = {}
        prompt_by_severity: dict[str, Any] = {}
        for severity in SEVERITY_ORDER:
            text_by_severity[severity] = _run_json_script(
                TEXTO_SCRIPT,
                [
                    "--story-rel-path",
                    story_rel,
                    "--severity",
                    severity,
                    "--target-age",
                    str(target_age),
                ],
            )
        for severity in SEVERITY_ORDER:
            prompt_by_severity[severity] = _run_json_script(
                PROMPTS_SCRIPT,
                [
                    "--story-rel-path",
                    story_rel,
                    "--severity",
                    severity,
                    "--target-age",
                    str(target_age),
                ],
            )

        cierre = _run_json_script(
            CIERRE_SCRIPT,
            [
                "--story-rel-path",
                story_rel,
            ],
        )
        stories_summary.append(
            {
                "story_id": story_row.get("story_id"),
                "title": story_row.get("title"),
                "story_rel_path": story_rel,
                "text": {
                    severity: {
                        "findings_count": len(text_by_severity[severity].get("findings", [])),
                        "open_counts": text_by_severity[severity].get("open_counts", {}),
                    }
                    for severity in SEVERITY_ORDER
                },
                "prompts": {
                    severity: {
                        "findings_count": len(prompt_by_severity[severity].get("findings", [])),
                        "open_counts": prompt_by_severity[severity].get("open_counts", {}),
                    }
                    for severity in SEVERITY_ORDER
                },
                "cierre": cierre,
            }
        )

    definitive_count = sum(1 for story in stories_summary if story.get("cierre", {}).get("status") == "definitive")
    blocked_count = len(stories_summary) - definitive_count
    return {
        "ok": True,
        "book_rel_path": book_rel_path,
        "target_age": target_age,
        "contexto": contexto,
        "stories": stories_summary,
        "metrics": {
            "stories_total": len(stories_summary),
            "definitive": definitive_count,
            "in_review": blocked_count,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Orquestar contexto->texto->prompts->cierre sin logica en app/.")
    parser.add_argument("--inbox-book-title", required=True, help="Nombre de carpeta en library/_inbox.")
    parser.add_argument("--book-rel-path", required=True, help="Ruta relativa de libro en library/.")
    parser.add_argument("--target-age", required=True, type=int, help="Edad objetivo obligatoria.")
    args = parser.parse_args()

    try:
        result = run(
            inbox_book_title=args.inbox_book_title,
            book_rel_path=args.book_rel_path,
            target_age=args.target_age,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

