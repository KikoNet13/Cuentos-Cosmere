from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEVERITIES = ("critical", "major", "minor", "info")
REVIEW_SCHEMA_VERSION = "2.0"

_PAGE_HEADER_RE = re.compile(r"(?mi)^##\s*p[áa]gina\s+(\d{1,3})\s*$")
_TITLE_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_repo_root(start: Path | None = None) -> Path:
    cursor = (start or Path(__file__).resolve()).resolve()
    for candidate in [cursor, *cursor.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "library").exists():
            return candidate
    return Path.cwd().resolve()


REPO_ROOT = find_repo_root(Path(__file__).resolve())
LIBRARY_ROOT = REPO_ROOT / "library"


def slugify(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return token or "book"


def normalize_rel_path(path_text: str) -> str:
    normalized = path_text.strip().replace("\\", "/").lstrip("/")
    if normalized.startswith("library/"):
        normalized = normalized[len("library/") :]
    return normalized


def story_json_path(story_rel_path: str) -> Path:
    rel = normalize_rel_path(story_rel_path)
    if not rel:
        raise ValueError("story_rel_path no puede estar vacio")
    rel_path = Path(rel)
    if rel_path.suffix.lower() != ".json":
        rel_path = Path(f"{rel}.json")
    return LIBRARY_ROOT / rel_path


def story_rel_path_no_ext(story_path: Path) -> str:
    rel = story_path.relative_to(LIBRARY_ROOT).as_posix()
    if rel.endswith(".json"):
        rel = rel[:-5]
    return rel


def story_id_from_story_path(story_path: Path) -> str:
    story_id = story_path.stem
    if not re.fullmatch(r"\d{2}", story_id):
        raise ValueError(f"story_id invalido en ruta: {story_path}")
    return story_id


def reviews_dir_for_story(story_path: Path) -> Path:
    return story_path.parent / "_reviews"


def review_path_for_story(story_path: Path) -> Path:
    return reviews_dir_for_story(story_path) / f"{story_id_from_story_path(story_path)}.review.json"


def decisions_log_path_for_story(story_path: Path) -> Path:
    return reviews_dir_for_story(story_path) / f"{story_id_from_story_path(story_path)}.decisions.log.jsonl"


def read_text_with_fallback(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _extract_code_block(section: str, labels: list[str]) -> str:
    for label in labels:
        for pattern in (
            rf"(?is){label}\s*:\s*```(?:text)?\s*(.*?)\s*```",
            rf"(?is){label}\s*```(?:text)?\s*(.*?)\s*```",
        ):
            match = re.search(pattern, section)
            if match:
                return match.group(1).strip()
    code = re.search(r"(?is)```(?:text)?\s*(.*?)\s*```", section)
    if code:
        return code.group(1).strip()
    return ""


def parse_inbox_story_markdown(markdown_path: Path) -> dict[str, Any]:
    raw_text = read_text_with_fallback(markdown_path)
    title_match = _TITLE_RE.search(raw_text)
    story_title = title_match.group(1).strip() if title_match else f"Cuento {markdown_path.stem}"
    story_id_match = re.search(r"(\d{2})", markdown_path.stem)
    if not story_id_match:
        raise ValueError(f"No se pudo inferir story_id en {markdown_path}")
    story_id = story_id_match.group(1)

    page_matches = list(_PAGE_HEADER_RE.finditer(raw_text))
    if not page_matches:
        raise ValueError(f"No se detectaron bloques '## Pagina NN' en {markdown_path}")

    pages: list[dict[str, Any]] = []
    for index, match in enumerate(page_matches):
        page_number = int(match.group(1))
        start = match.end()
        end = page_matches[index + 1].start() if index + 1 < len(page_matches) else len(raw_text)
        section = raw_text[start:end]
        text_block = _extract_code_block(section, [r"texto"])
        image_block = _extract_code_block(section, [r"imagen"])
        pages.append(
            {
                "page_number": page_number,
                "text": text_block,
                "prompt_main": image_block,
            }
        )

    pages.sort(key=lambda item: item["page_number"])
    return {
        "story_id": story_id,
        "title": story_title,
        "pages": pages,
    }


def build_story_payload(
    *,
    story_id: str,
    title: str,
    book_rel_path: str,
    pages: list[dict[str, Any]],
    created_at: str | None = None,
) -> dict[str, Any]:
    timestamp = created_at or utc_now_iso()
    rendered_pages: list[dict[str, Any]] = []
    for page in sorted(pages, key=lambda item: item["page_number"]):
        text_value = page.get("text", "").strip()
        prompt_main = page.get("prompt_main", "").strip()
        rendered_pages.append(
            {
                "page_number": int(page["page_number"]),
                "status": "draft",
                "text": {
                    "original": text_value,
                    "current": text_value,
                },
                "images": {
                    "main": {
                        "slot_name": "main",
                        "status": "draft",
                        "prompt": {
                            "original": prompt_main,
                            "current": prompt_main,
                        },
                        "active_id": "",
                        "alternatives": [],
                    }
                },
            }
        )

    return {
        "schema_version": "1.0",
        "story_id": story_id,
        "title": title,
        "status": "draft",
        "book_rel_path": normalize_rel_path(book_rel_path),
        "created_at": timestamp,
        "updated_at": utc_now_iso(),
        "pages": rendered_pages,
    }


def resolve_inbox_book_dir(inbox_book_title: str) -> Path:
    inbox_root = LIBRARY_ROOT / "_inbox"
    direct = inbox_root / inbox_book_title
    if direct.exists() and direct.is_dir():
        return direct

    wanted = slugify(inbox_book_title)
    for candidate in sorted(inbox_root.iterdir(), key=lambda path: path.name.lower()):
        if candidate.is_dir() and slugify(candidate.name) == wanted:
            return candidate
    raise FileNotFoundError(f"No existe inbox para '{inbox_book_title}' en {inbox_root}")


def list_inbox_story_markdowns(inbox_book_title: str) -> list[Path]:
    book_dir = resolve_inbox_book_dir(inbox_book_title)
    candidates: list[Path] = []
    for file_path in book_dir.rglob("*.md"):
        parts = {segment.lower() for segment in file_path.parts}
        if "_ignore" in parts:
            continue
        if not re.fullmatch(r"\d{2}\.md", file_path.name.lower()):
            continue
        candidates.append(file_path)

    def sort_key(path: Path) -> tuple[int, int, str]:
        root_priority = 0 if path.parent == book_dir else 1
        number = int(path.stem) if path.stem.isdigit() else 999
        return (root_priority, number, path.as_posix())

    return sorted(candidates, key=sort_key)


def cleanup_legacy_sidecars(book_dir: Path) -> list[str]:
    reviews_dir = book_dir / "_reviews"
    if not reviews_dir.exists():
        return []

    removed: list[str] = []
    legacy_files = (
        "context_chain.json",
        "glossary_merged.json",
        "context_review.json",
        "adaptation_profile.json",
        "pipeline_state.json",
    )
    for filename in legacy_files:
        file_path = reviews_dir / filename
        if file_path.exists():
            file_path.unlink()
            removed.append(file_path.relative_to(REPO_ROOT).as_posix())

    legacy_patterns = (
        "*.findings.json",
        "*.choices.json",
        "*.contrast.json",
        "*.passes.json",
        "*.review.md",
        "*.decisions.json",
    )
    for pattern in legacy_patterns:
        for file_path in reviews_dir.glob(pattern):
            if file_path.exists():
                file_path.unlink()
                removed.append(file_path.relative_to(REPO_ROOT).as_posix())
    return sorted(set(removed))


def _default_open_counts() -> dict[str, int]:
    return {severity: 0 for severity in SEVERITIES}


def _ensure_metrics(review: dict[str, Any]) -> dict[str, Any]:
    raw_metrics = review.get("metrics", {}) if isinstance(review.get("metrics"), dict) else {}
    raw_runs = raw_metrics.get("runs", {}) if isinstance(raw_metrics.get("runs"), dict) else {}
    runs: dict[str, int] = {}
    for key in ("contexto", "texto", "prompts", "cierre"):
        runs[key] = int(raw_runs.get(key, 0))
    metrics = {
        "runs": runs,
        "findings_detected_total": int(raw_metrics.get("findings_detected_total", 0)),
        "decisions_applied_total": int(raw_metrics.get("decisions_applied_total", 0)),
    }
    review["metrics"] = metrics
    return metrics


def recompute_open_counts(review: dict[str, Any]) -> dict[str, int]:
    counts = _default_open_counts()
    for finding in review.get("findings", []):
        if finding.get("status") != "open":
            continue
        severity = finding.get("severity")
        if severity in counts:
            counts[severity] += 1
    review["open_counts"] = counts
    return counts


def ensure_review_contract(
    story_path: Path,
    *,
    target_age: int | None = None,
    phase: str | None = None,
    severity_cursor: str | None = None,
) -> dict[str, Any]:
    story = load_json(story_path)
    review_path = review_path_for_story(story_path)
    review_existing = load_json(review_path, default={}) if review_path.exists() else {}

    review = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "story_id": story.get("story_id") or story_id_from_story_path(story_path),
        "story_rel_path": story_rel_path_no_ext(story_path),
        "status": review_existing.get("status", "in_review"),
        "target_age": target_age if target_age is not None else review_existing.get("target_age"),
        "phase": phase or review_existing.get("phase", "contexto"),
        "severity_cursor": severity_cursor or review_existing.get("severity_cursor"),
        "open_counts": review_existing.get("open_counts", _default_open_counts()),
        "findings": review_existing.get("findings", []),
        "decisions": review_existing.get("decisions", []),
        "metrics": review_existing.get("metrics", {}),
        "updated_at": utc_now_iso(),
    }
    _ensure_metrics(review)
    recompute_open_counts(review)
    return review


def save_review(story_path: Path, review: dict[str, Any]) -> Path:
    review["updated_at"] = utc_now_iso()
    recompute_open_counts(review)
    review_path = review_path_for_story(story_path)
    save_json(review_path, review)
    return review_path


def upsert_open_findings(
    review: dict[str, Any],
    *,
    stage: str,
    severity: str,
    findings: list[dict[str, Any]],
) -> None:
    retained: list[dict[str, Any]] = []
    for finding in review.get("findings", []):
        same_band = finding.get("stage") == stage and finding.get("severity") == severity and finding.get("status") == "open"
        if not same_band:
            retained.append(finding)
    retained.extend(findings)
    review["findings"] = retained
    metrics = _ensure_metrics(review)
    metrics["findings_detected_total"] += len(findings)
    recompute_open_counts(review)


def next_option_letter(index: int) -> str:
    return chr(ord("A") + index)


def build_finding_id(
    *,
    stage: str,
    severity: str,
    page_number: int,
    issue_type: str,
    content: str,
) -> str:
    base = f"{stage}|{severity}|{page_number}|{issue_type}|{content}".encode("utf-8", errors="ignore")
    suffix = hashlib.sha1(base).hexdigest()[:10]
    return f"{stage}-{severity}-p{page_number:02d}-{suffix}"


def parse_apply_decisions(raw_value: str | None) -> list[dict[str, Any]]:
    if not raw_value:
        return []
    candidate_path = Path(raw_value)
    if candidate_path.exists():
        parsed = json.loads(read_text_with_fallback(candidate_path))
    else:
        parsed = json.loads(raw_value)
    if isinstance(parsed, dict):
        if isinstance(parsed.get("decisions"), list):
            parsed = parsed["decisions"]
        else:
            parsed = [parsed]
    if not isinstance(parsed, list):
        raise ValueError("apply-decision-json debe ser objeto, lista o archivo JSON valido")
    normalized: list[dict[str, Any]] = []
    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError("cada decision debe ser un objeto")
        normalized.append(item)
    return normalized


def resolve_option_value(
    finding: dict[str, Any],
    *,
    selected_option: str,
    custom_value: str | None,
) -> str:
    option = (selected_option or "A").strip().upper()
    proposals = finding.get("proposals", [])
    if option == "D":
        final_value = (custom_value or "").strip()
        if not final_value:
            raise ValueError(f"La decision D requiere valor libre para {finding.get('finding_id')}")
        return final_value
    for proposal in proposals:
        if str(proposal.get("option", "")).upper() == option:
            value = str(proposal.get("value", "")).strip()
            if value:
                return value
            break
    raise ValueError(f"Opcion {option} no valida para {finding.get('finding_id')}")


def ensure_story_from_markdown(book_rel_path: str, markdown_path: Path) -> Path:
    parsed = parse_inbox_story_markdown(markdown_path)
    normalized_book = normalize_rel_path(book_rel_path)
    story_path = LIBRARY_ROOT / normalized_book / f"{parsed['story_id']}.json"
    if story_path.exists():
        return story_path

    payload = build_story_payload(
        story_id=parsed["story_id"],
        title=parsed["title"],
        book_rel_path=normalized_book,
        pages=parsed["pages"],
    )
    save_json(story_path, payload)
    return story_path


def update_story_status(story_payload: dict[str, Any], status: str) -> None:
    story_payload["status"] = status
    story_payload["updated_at"] = utc_now_iso()
