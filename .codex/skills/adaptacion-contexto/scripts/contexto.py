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
    LIBRARY_ROOT,
    cleanup_legacy_sidecars,
    list_inbox_story_markdowns,
    normalize_rel_path,
    parse_inbox_story_markdown,
    resolve_inbox_book_dir,
)


def _age_profile(target_age: int) -> dict[str, Any]:
    if target_age <= 6:
        band = "5-6"
        max_sentence = 14
    elif target_age <= 8:
        band = "7-8"
        max_sentence = 18
    elif target_age <= 10:
        band = "9-10"
        max_sentence = 22
    else:
        band = "11+"
        max_sentence = 28
    return {
        "target_age": target_age,
        "reading_band": band,
        "max_sentence_words": max_sentence,
        "tone": "aventura clara y comprensible",
        "safety": "sin violencia grafica, sin sexualizacion, sin gore",
    }


def run(inbox_book_title: str, book_rel_path: str, target_age: int) -> dict[str, Any]:
    inbox_dir = resolve_inbox_book_dir(inbox_book_title)
    story_markdowns = list_inbox_story_markdowns(inbox_book_title)
    story_rows: list[dict[str, Any]] = []
    for md_path in story_markdowns:
        parsed = parse_inbox_story_markdown(md_path)
        pdf_path = md_path.with_suffix(".pdf")
        story_rows.append(
            {
                "story_id": parsed["story_id"],
                "title": parsed["title"],
                "pages_detected": len(parsed["pages"]),
                "markdown_rel_path": md_path.relative_to(REPO_ROOT).as_posix(),
                "pdf_rel_path": pdf_path.relative_to(REPO_ROOT).as_posix() if pdf_path.exists() else None,
            }
        )

    normalized_book_rel = normalize_rel_path(book_rel_path)
    target_book_dir = LIBRARY_ROOT / normalized_book_rel
    target_book_dir.mkdir(parents=True, exist_ok=True)
    removed_sidecars = cleanup_legacy_sidecars(target_book_dir)

    payload = {
        "ok": True,
        "book_rel_path": normalized_book_rel,
        "target_age": target_age,
        "inventory": {
            "inbox_book_title": inbox_book_title,
            "inbox_rel_path": inbox_dir.relative_to(REPO_ROOT).as_posix(),
            "stories": story_rows,
            "count": len(story_rows),
        },
        "age_profile": _age_profile(target_age),
        "context_base": {
            "phase_order": ["contexto", "texto", "prompts", "cierre"],
            "severity_order": ["critical", "major", "minor", "info"],
            "required_visual_slot": "prompt.main",
        },
        "legacy_cleanup": {
            "removed_files": removed_sidecars,
        },
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Preparar contexto base de adaptacion editorial por libro.")
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

