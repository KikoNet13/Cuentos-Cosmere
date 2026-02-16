#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean
from typing import Any

STORY_FILE_RE = re.compile(r"^(\d{2})\.md$", re.IGNORECASE)
PAGE_HEADING_RE = re.compile(r"(?im)^##\s*P[aá]gina\s+(\d{1,3})\s*$")
SEVERITIES = ("critical", "major", "minor", "info")

CONTEXT_SCHEMA_VERSION = "1.1"
ISSUES_SCHEMA_VERSION = "1.1"
STORY_SCHEMA_VERSION = "1.1"

ANALYSIS_POLICY = {
    "canon_priority": "pdf",
    "batch_blocking": "all_or_nothing",
    "ocr_policy": "optional_with_blocking_if_unreadable",
    "age_mode": "balanced",
}

GLOSSARY_REASON_PRIORITY = ("variant_conflict", "pdf_only_term", "md_only_term", "entity_term")
CANON_OVERLAP_THRESHOLD = 0.12

COMMON_STOPWORDS = {
    "a",
    "al",
    "algo",
    "alli",
    "alli",
    "alla",
    "ante",
    "antes",
    "aqui",
    "asi",
    "aun",
    "bajo",
    "bien",
    "cada",
    "como",
    "con",
    "contra",
    "cual",
    "cuales",
    "cualquier",
    "de",
    "del",
    "desde",
    "donde",
    "dos",
    "el",
    "ella",
    "ellas",
    "ellos",
    "en",
    "entre",
    "era",
    "eres",
    "es",
    "esa",
    "esas",
    "ese",
    "eso",
    "esos",
    "esta",
    "estaba",
    "estan",
    "estar",
    "este",
    "esto",
    "estos",
    "fue",
    "ha",
    "han",
    "hay",
    "hasta",
    "la",
    "las",
    "le",
    "les",
    "lo",
    "los",
    "mas",
    "mi",
    "mis",
    "muy",
    "ni",
    "no",
    "nos",
    "nuestra",
    "nuestro",
    "o",
    "os",
    "otra",
    "otro",
    "para",
    "pero",
    "por",
    "que",
    "quien",
    "se",
    "si",
    "sin",
    "sobre",
    "su",
    "sus",
    "te",
    "tenia",
    "ti",
    "tu",
    "tus",
    "un",
    "una",
    "uno",
    "unos",
    "ya",
    "y",
}

ENTITY_BLACKLIST = {
    "El",
    "La",
    "Los",
    "Las",
    "Un",
    "Una",
    "Uno",
    "Y",
    "Pero",
    "Mientras",
    "Entonces",
    "Cuando",
    "Todo",
    "Todos",
    "Esta",
    "Este",
    "Eso",
}

AGE_CHILDISH_MARKERS = (
    "super",
    "pum",
    "zis",
    "zas",
    "pequena",
    "pequeno",
    "amig",
    "heroina",
    "heroe",
    "magia",
    "brill",
)

QUOTE_PATTERNS = (
    re.compile(r'"([^"\n]{3,120})"'),
    re.compile(r"«([^»\n]{3,120})»"),
)
ENTITY_RE = re.compile(
    r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}){0,2}\b"
)


@dataclass
class StorySource:
    story_id: str
    md_path: Path
    pdf_path: Path


@dataclass
class PdfStoryData:
    story_id: str
    pages_text: list[str]
    backend: str
    ocr_pages: list[int]
    page_sources: dict[int, str]
    parser_chain: list[str]
    pdf_rel_path: str


@dataclass
class TermEvidence:
    key: str
    term: str
    variants: set[str] = field(default_factory=set)
    md_variants: set[str] = field(default_factory=set)
    pdf_variants: set[str] = field(default_factory=set)
    md_pages_by_story: dict[str, set[int]] = field(default_factory=lambda: defaultdict(set))
    pdf_pages_by_story: dict[str, set[int]] = field(default_factory=lambda: defaultdict(set))
    reasons: set[str] = field(default_factory=set)
    is_entity: bool = False

    def source_presence(self) -> str:
        has_md = any(self.md_pages_by_story.values())
        has_pdf = any(self.pdf_pages_by_story.values())
        if has_md and has_pdf:
            return "both"
        if has_pdf:
            return "pdf"
        return "md"

    def all_pages(self) -> list[int]:
        pages: set[int] = set()
        for values in self.md_pages_by_story.values():
            pages.update(values)
        for values in self.pdf_pages_by_story.values():
            pages.update(values)
        return sorted(pages)


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


def normalize_for_compare(raw_value: str) -> str:
    value = unicodedata.normalize("NFKD", raw_value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)


def clean_space(raw_value: str) -> str:
    return re.sub(r"\s+", " ", raw_value).strip()


def excerpt(raw_value: str, limit: int = 180) -> str:
    compact = clean_space(raw_value)
    if len(compact) <= limit:
        return compact
    return f"{compact[: max(limit - 3, 0)]}..."


def tokenize_words(raw_value: str, min_len: int = 3) -> set[str]:
    words = re.findall(rf"[A-Za-z0-9ÁÉÍÓÚÑáéíóúñ]{{{min_len},}}", raw_value)
    return {clean_space(word).lower() for word in words if clean_space(word)}


def informative_tokens(raw_value: str) -> set[str]:
    result: set[str] = set()
    for token in tokenize_words(raw_value, min_len=3):
        normalized = normalize_for_compare(token)
        if not normalized:
            continue
        if normalized in COMMON_STOPWORDS:
            continue
        if len(normalized) < 3:
            continue
        result.add(normalized)
    return result


def split_sentences(raw_value: str) -> list[str]:
    candidates = re.split(r"[.!?]+", raw_value)
    return [clean_space(item) for item in candidates if clean_space(item)]


def has_usable_text(raw_value: str) -> bool:
    if len(clean_space(raw_value)) < 12:
        return False
    return len(tokenize_words(raw_value, min_len=2)) >= 3


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
    source: dict[str, Any] | None = None,
    detector: str | None = None,
    confidence: float | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "issue_id": f"{story_id}-I{index:03d}",
        "severity": severity,
        "category": category,
        "page_number": page_number,
        "evidence": evidence.strip(),
        "suggested_action": suggested_action.strip(),
        "status": status,
    }
    if source:
        payload["source"] = source
    if detector:
        payload["detector"] = detector
    if confidence is not None:
        payload["confidence"] = max(0.0, min(round(float(confidence), 3), 1.0))
    return payload


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
        sources.append(StorySource(story_id=story_id, md_path=md_path, pdf_path=md_path.with_suffix(".pdf")))
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

def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def detect_ocr_support() -> dict[str, Any]:
    pdf2image_ok = module_available("pdf2image")
    pytesseract_ok = module_available("pytesseract")
    tesseract_bin = shutil.which("tesseract")
    return {
        "pdf2image": pdf2image_ok,
        "pytesseract": pytesseract_ok,
        "tesseract_bin": bool(tesseract_bin),
        "ready": pdf2image_ok and pytesseract_ok and bool(tesseract_bin),
        "tesseract_path": tesseract_bin or "",
    }


def read_pdf_with_pdfplumber(pdf_path: Path) -> tuple[list[str] | None, str | None]:
    if not module_available("pdfplumber"):
        return None, "module_missing"
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(str(pdf_path)) as pdf:
            pages = [(page.extract_text() or "").strip() for page in pdf.pages]
        return pages, None
    except Exception as exc:  # pragma: no cover - depends on local parser internals
        return None, str(exc)


def read_pdf_with_pypdf(pdf_path: Path) -> tuple[list[str] | None, str | None]:
    if not module_available("pypdf"):
        return None, "module_missing"
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(pdf_path))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        return pages, None
    except Exception as exc:  # pragma: no cover - depends on local parser internals
        return None, str(exc)


def run_ocr_page(pdf_path: Path, page_number: int) -> tuple[str | None, str | None]:
    try:
        from pdf2image import convert_from_path  # type: ignore
        import pytesseract  # type: ignore
    except Exception as exc:
        return None, str(exc)

    try:
        images = convert_from_path(
            str(pdf_path),
            first_page=page_number,
            last_page=page_number,
            fmt="png",
            single_file=True,
        )
        if not images:
            return None, "No se pudo renderizar la pagina para OCR."
        text = pytesseract.image_to_string(images[0], lang="spa+eng")
        return (text or "").strip(), None
    except Exception as exc:  # pragma: no cover - depends on local poppler/tesseract runtime
        return None, str(exc)


def preflight_story_pdf(source: StorySource, root_dir: Path) -> tuple[PdfStoryData | None, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []

    def add_error(
        *,
        code: str,
        message: str,
        page_number: int | None = None,
    ) -> None:
        payload: dict[str, Any] = {"code": code, "story_id": source.story_id, "message": message}
        if page_number is not None:
            payload["page_number"] = page_number
        errors.append(payload)

    if not source.pdf_path.exists():
        add_error(
            code="input.missing_pdf",
            message=f"No existe PDF de referencia para {source.pdf_path.name}.",
        )
        return None, errors

    parser_chain: list[str] = []
    pages_text: list[str] | None = None
    backend = ""

    plumber_pages, plumber_error = read_pdf_with_pdfplumber(source.pdf_path)
    if plumber_error == "module_missing":
        parser_chain.append("pdfplumber:missing")
    elif plumber_error:
        parser_chain.append(f"pdfplumber:error:{plumber_error}")
    else:
        pages_text = plumber_pages
        backend = "pdfplumber"
        parser_chain.append("pdfplumber:ok")

    if pages_text is None:
        pypdf_pages, pypdf_error = read_pdf_with_pypdf(source.pdf_path)
        if pypdf_error == "module_missing":
            parser_chain.append("pypdf:missing")
        elif pypdf_error:
            parser_chain.append(f"pypdf:error:{pypdf_error}")
        else:
            pages_text = pypdf_pages
            backend = "pypdf"
            parser_chain.append("pypdf:ok")

    if pages_text is None:
        has_pdfplumber = module_available("pdfplumber")
        has_pypdf = module_available("pypdf")
        if not has_pdfplumber and not has_pypdf:
            add_error(
                code="pdf.parser_unavailable",
                message="No hay parser PDF disponible (instala pdfplumber o pypdf).",
            )
        else:
            details = "; ".join(parser_chain) if parser_chain else "sin detalles"
            add_error(
                code="pdf.unreadable",
                message=f"No se pudo extraer texto del PDF con parsers disponibles ({details}).",
            )
        return None, errors

    if not pages_text:
        add_error(code="pdf.unreadable", message="El PDF no contiene paginas legibles por parser.")
        return None, errors

    ocr_support = detect_ocr_support()
    used_ocr_pages: list[int] = []
    page_sources: dict[int, str] = {}
    ocr_runtime_error: str | None = None

    for index, page_text in enumerate(pages_text, start=1):
        page_sources[index] = backend
        if has_usable_text(page_text):
            continue

        if ocr_support["ready"]:
            ocr_text, ocr_error = run_ocr_page(source.pdf_path, index)
            if ocr_text and has_usable_text(ocr_text):
                pages_text[index - 1] = ocr_text
                page_sources[index] = "ocr"
                used_ocr_pages.append(index)
                continue
            if ocr_error:
                ocr_runtime_error = ocr_error

        if not has_usable_text(pages_text[index - 1]):
            if ocr_support["ready"]:
                reason = "OCR no devolvio texto util."
                if ocr_runtime_error:
                    reason = f"OCR fallo: {ocr_runtime_error}"
            else:
                reason = (
                    "Pagina sin texto util y OCR no disponible "
                    "(requiere pdf2image + pytesseract + binario tesseract)."
                )
            add_error(
                code="pdf.page_unreadable",
                message=f"Pagina {index} sin cobertura util en {source.pdf_path.name}. {reason}",
                page_number=index,
            )

    if errors:
        return None, errors

    return (
        PdfStoryData(
            story_id=source.story_id,
            pages_text=pages_text,
            backend=backend,
            ocr_pages=used_ocr_pages,
            page_sources=page_sources,
            parser_chain=parser_chain,
            pdf_rel_path=normalize_rel(source.pdf_path, root_dir),
        ),
        errors,
    )


def extract_quotes(raw_value: str) -> set[str]:
    terms: set[str] = set()
    for pattern in QUOTE_PATTERNS:
        for match in pattern.findall(raw_value):
            cleaned = clean_space(match)
            if len(cleaned) < 3:
                continue
            if len(cleaned.split()) > 10:
                continue
            terms.add(cleaned)
    return terms


def extract_entities(raw_value: str) -> set[str]:
    entities: set[str] = set()
    for match in ENTITY_RE.findall(raw_value):
        candidate = clean_space(match)
        if not candidate:
            continue
        if candidate in ENTITY_BLACKLIST:
            continue
        words = candidate.split()
        if any(len(word) < 3 for word in words):
            continue
        entities.add(candidate)
    return entities


def extract_numbers(raw_value: str) -> set[str]:
    values = re.findall(r"\b\d+(?:[.,]\d+)?\b", raw_value)
    return {clean_space(item) for item in values if clean_space(item)}


def is_noise_term(term: str) -> bool:
    normalized = normalize_for_compare(term)
    if not normalized:
        return True
    words = normalized.split()
    if len(words) == 0:
        return True
    if len(words) > 8:
        return True
    if all(word in COMMON_STOPWORDS for word in words):
        return True
    if normalized.startswith("pagina "):
        return True
    if normalized in {"portada", "texto", "imagen"}:
        return True
    if re.fullmatch(r"\d+(?:\s+\d+)*", normalized):
        return True
    return False


def register_term(
    evidence_by_key: dict[str, TermEvidence],
    *,
    term: str,
    source_kind: str,
    story_id: str,
    page_number: int,
    is_entity: bool,
) -> None:
    cleaned = clean_space(term)
    if not cleaned or is_noise_term(cleaned):
        return
    key = slugify(normalize_for_compare(cleaned))
    if not key:
        return

    entry = evidence_by_key.get(key)
    if entry is None:
        entry = TermEvidence(key=key, term=cleaned)
        evidence_by_key[key] = entry

    if len(cleaned) < len(entry.term):
        entry.term = cleaned

    entry.variants.add(cleaned)
    entry.is_entity = entry.is_entity or is_entity
    if source_kind == "md":
        entry.md_variants.add(cleaned)
        entry.md_pages_by_story[story_id].add(page_number)
    else:
        entry.pdf_variants.add(cleaned)
        entry.pdf_pages_by_story[story_id].add(page_number)


def collect_term_evidence(
    parsed_stories: dict[str, dict[str, Any]],
    pdf_data_by_story: dict[str, PdfStoryData],
) -> dict[str, TermEvidence]:
    evidence_by_key: dict[str, TermEvidence] = {}

    for story_id, parsed_story in parsed_stories.items():
        for page in parsed_story.get("pages", []):
            page_number = int(page.get("page_number", 0))
            md_chunks = [str(page.get("text_original", "")), str(page.get("prompt_original", ""))]
            md_joined = "\n".join(md_chunks)
            for quoted in extract_quotes(md_joined):
                register_term(
                    evidence_by_key,
                    term=quoted,
                    source_kind="md",
                    story_id=story_id,
                    page_number=page_number,
                    is_entity=False,
                )
            for entity in extract_entities(md_joined):
                register_term(
                    evidence_by_key,
                    term=entity,
                    source_kind="md",
                    story_id=story_id,
                    page_number=page_number,
                    is_entity=True,
                )

    for story_id, pdf_data in pdf_data_by_story.items():
        for page_number, page_text in enumerate(pdf_data.pages_text, start=1):
            for quoted in extract_quotes(page_text):
                register_term(
                    evidence_by_key,
                    term=quoted,
                    source_kind="pdf",
                    story_id=story_id,
                    page_number=page_number,
                    is_entity=False,
                )
            for entity in extract_entities(page_text):
                register_term(
                    evidence_by_key,
                    term=entity,
                    source_kind="pdf",
                    story_id=story_id,
                    page_number=page_number,
                    is_entity=True,
                )

    for evidence in evidence_by_key.values():
        has_md = any(evidence.md_pages_by_story.values())
        has_pdf = any(evidence.pdf_pages_by_story.values())
        if has_md and has_pdf:
            md_norm = {normalize_for_compare(item) for item in evidence.md_variants if normalize_for_compare(item)}
            pdf_norm = {normalize_for_compare(item) for item in evidence.pdf_variants if normalize_for_compare(item)}
            if md_norm and pdf_norm and md_norm != pdf_norm:
                evidence.reasons.add("variant_conflict")
        elif has_pdf:
            evidence.reasons.add("pdf_only_term")
        else:
            evidence.reasons.add("md_only_term")

        if evidence.is_entity:
            evidence.reasons.add("entity_term")

    return evidence_by_key


def choose_glossary_reason(reasons: set[str]) -> str:
    for candidate in GLOSSARY_REASON_PRIORITY:
        if candidate in reasons:
            return candidate
    return "entity_term"


def build_ambiguous_terms(evidence_by_key: dict[str, TermEvidence]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for entry in evidence_by_key.values():
        if not entry.reasons:
            continue
        reason = choose_glossary_reason(entry.reasons)
        items.append(
            {
                "key": entry.key,
                "term": entry.term,
                "reason": reason,
                "reasons": sorted(entry.reasons),
                "variants": sorted(entry.variants, key=lambda value: value.casefold()),
                "source_presence": entry.source_presence(),
                "evidence_pages": entry.all_pages(),
            }
        )
    items.sort(key=lambda item: str(item["term"]).casefold())
    return items


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
    ambiguous_terms: list[dict[str, Any]],
    glossary_answers: dict[str, Any],
    canon_sources: list[dict[str, Any]],
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

    for item in ambiguous_terms:
        term = str(item.get("term", "")).strip()
        if not term:
            continue
        confirmed_value = glossary_answer_for(term, glossary_answers)
        previous = glossary_map.get(term, {})
        canonical = confirmed_value
        status = "confirmed" if canonical else "pending"
        if not canonical and previous.get("status") == "confirmed":
            canonical = str(previous.get("canonical", "")).strip()
            status = "confirmed" if canonical else "pending"
        glossary_map[term] = {
            "term": term,
            "status": status,
            "canonical": canonical,
            "variants": list(item.get("variants", [])),
            "source_presence": str(item.get("source_presence", "md")),
            "evidence_pages": list(item.get("evidence_pages", [])),
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
        if item.get("status") != "confirmed"
    ]

    notes = [
        f"Ingesta inicial actualizada {utc_now_iso()}",
        "Contraste canonico obligatorio contra PDF de referencia.",
    ]

    return {
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "book_rel_path": book_rel_path,
        "book_title": book_title,
        "target_age": target_age,
        "updated_at": utc_now_iso(),
        "analysis_policy": dict(ANALYSIS_POLICY),
        "canon_sources": canon_sources,
        "stories": sorted(all_story_rel),
        "glossary": glossary_items,
        "ambiguities": ambiguities,
        "notes": notes,
    }


def build_source_snapshot(
    *,
    md_page: int | None,
    pdf_page: int | None,
    md_text: str,
    pdf_text: str,
) -> dict[str, Any]:
    return {
        "md_page_number": md_page,
        "pdf_page_number": pdf_page,
        "md_excerpt": excerpt(md_text),
        "pdf_excerpt": excerpt(pdf_text),
    }


def age_page_metrics(raw_value: str) -> dict[str, float]:
    sentences = split_sentences(raw_value)
    sentence_lengths: list[float] = []
    for sentence in sentences:
        words = tokenize_words(sentence, min_len=1)
        if words:
            sentence_lengths.append(float(len(words)))
    words = tokenize_words(raw_value, min_len=1)
    words_count = max(len(words), 1)

    long_words = sum(1 for word in words if len(word) >= 10)
    exclamations = raw_value.count("!")
    normalized_words = [normalize_for_compare(word) for word in words]
    childish_hits = 0
    for word in normalized_words:
        for marker in AGE_CHILDISH_MARKERS:
            if marker in word:
                childish_hits += 1
                break

    return {
        "avg_sentence_length": fmean(sentence_lengths) if sentence_lengths else 0.0,
        "long_word_ratio": long_words / words_count,
        "exclamation_ratio": exclamations / words_count,
        "childish_marker_ratio": childish_hits / words_count,
    }


def detect_age_category(page_metrics: dict[str, float], target_age: int) -> tuple[str | None, str, float]:
    avg_sentence = page_metrics["avg_sentence_length"]
    long_ratio = page_metrics["long_word_ratio"]
    exclamation_ratio = page_metrics["exclamation_ratio"]
    childish_ratio = page_metrics["childish_marker_ratio"]

    if target_age <= 7:
        if avg_sentence > 16 or long_ratio > 0.17:
            confidence = min(1.0, max((avg_sentence - 16) / 8.0, (long_ratio - 0.17) / 0.15) + 0.4)
            return (
                "age.too_complex",
                "Texto con complejidad superior al rango infantil objetivo.",
                confidence,
            )
        return None, "", 0.0

    if target_age <= 10:
        if avg_sentence > 20 or long_ratio > 0.20:
            confidence = min(1.0, max((avg_sentence - 20) / 8.0, (long_ratio - 0.20) / 0.12) + 0.35)
            return (
                "age.too_complex",
                "Texto potencialmente complejo para la edad objetivo.",
                confidence,
            )
        if childish_ratio > 0.055 and avg_sentence < 11:
            confidence = min(1.0, ((childish_ratio - 0.055) / 0.08) + 0.3)
            return (
                "age.too_childish",
                "Texto posiblemente infantilizado para la edad objetivo.",
                confidence,
            )
        return None, "", 0.0

    if avg_sentence > 24 or long_ratio > 0.23:
        confidence = min(1.0, max((avg_sentence - 24) / 9.0, (long_ratio - 0.23) / 0.1) + 0.3)
        return (
            "age.too_complex",
            "Texto con densidad alta para lectura objetivo.",
            confidence,
        )
    if (childish_ratio > 0.035 and avg_sentence < 12) or exclamation_ratio > 0.03:
        confidence = min(1.0, max((childish_ratio - 0.035) / 0.05, (exclamation_ratio - 0.03) / 0.05) + 0.25)
        return (
            "age.too_childish",
            "Texto posiblemente demasiado infantil para la edad objetivo.",
            confidence,
        )
    return None, "", 0.0


def detect_story_canonical_issues(
    *,
    source: StorySource,
    parsed_story: dict[str, Any],
    pdf_data: PdfStoryData,
    start_index: int,
    glossary_answers: dict[str, Any],
    target_age: int | None,
    term_evidence_by_key: dict[str, TermEvidence],
) -> tuple[list[dict[str, Any]], int, dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    next_index = start_index

    md_pages = sorted(parsed_story.get("pages", []), key=lambda item: int(item.get("page_number", 0)))
    pdf_pages = pdf_data.pages_text

    overlap_values: list[float] = []
    age_alerts = {"age.too_complex": 0, "age.too_childish": 0}
    detector_counts: Counter[str] = Counter()

    if len(md_pages) != len(pdf_pages):
        issues.append(
            build_issue(
                story_id=source.story_id,
                index=next_index,
                severity="major",
                category="pdf.page_count_mismatch",
                page_number=None,
                evidence=f"Markdown={len(md_pages)} paginas, PDF={len(pdf_pages)} paginas.",
                suggested_action="Revisar paginacion de propuesta vs PDF canon.",
                detector="page_count_v1",
                confidence=0.99,
            )
        )
        detector_counts["pdf.page_count_mismatch"] += 1
        next_index += 1

    for page in md_pages:
        page_number = int(page.get("page_number", 0))
        md_text = str(page.get("text_original", ""))
        pdf_text = pdf_pages[page_number - 1] if 1 <= page_number <= len(pdf_pages) else ""
        source_snapshot = build_source_snapshot(
            md_page=page_number,
            pdf_page=page_number if 1 <= page_number <= len(pdf_pages) else None,
            md_text=md_text,
            pdf_text=pdf_text,
        )

        md_tokens = informative_tokens(md_text)
        pdf_tokens = informative_tokens(pdf_text)
        if pdf_tokens:
            overlap = len(md_tokens.intersection(pdf_tokens)) / max(len(pdf_tokens), 1)
            overlap_values.append(overlap)
            if overlap < CANON_OVERLAP_THRESHOLD:
                severity = "critical" if overlap < 0.06 else "major"
                issues.append(
                    build_issue(
                        story_id=source.story_id,
                        index=next_index,
                        severity=severity,
                        category="canon.low_page_overlap",
                        page_number=page_number,
                        evidence=f"Solapamiento informativo bajo frente a canon PDF ({overlap:.2f}).",
                        suggested_action="Revisar contenido de pagina para alinearlo con el canon.",
                        source=source_snapshot,
                        detector="lexical_overlap_v2",
                        confidence=min(1.0, (CANON_OVERLAP_THRESHOLD - overlap) / CANON_OVERLAP_THRESHOLD + 0.35),
                    )
                )
                detector_counts["canon.low_page_overlap"] += 1
                next_index += 1

        md_entities = extract_entities(md_text)
        pdf_entities = extract_entities(pdf_text)
        missing_entities = sorted(pdf_entities.difference(md_entities), key=lambda value: value.casefold())
        extra_entities = sorted(md_entities.difference(pdf_entities), key=lambda value: value.casefold())

        if missing_entities:
            issues.append(
                build_issue(
                    story_id=source.story_id,
                    index=next_index,
                    severity="major",
                    category="canon.missing_entity",
                    page_number=page_number,
                    evidence=f"Entidades del canon ausentes en MD: {', '.join(missing_entities[:6])}.",
                    suggested_action="Reintroducir entidades canonicas clave o justificar la omision.",
                    source=source_snapshot,
                    detector="entity_diff_v1",
                    confidence=min(1.0, 0.45 + 0.08 * len(missing_entities)),
                )
            )
            detector_counts["canon.missing_entity"] += 1
            next_index += 1

        if extra_entities:
            issues.append(
                build_issue(
                    story_id=source.story_id,
                    index=next_index,
                    severity="minor",
                    category="canon.extra_entity",
                    page_number=page_number,
                    evidence=f"Entidades en MD no detectadas en canon PDF: {', '.join(extra_entities[:6])}.",
                    suggested_action="Validar si son alias permitidos o ruido de adaptacion.",
                    source=source_snapshot,
                    detector="entity_diff_v1",
                    confidence=min(1.0, 0.35 + 0.06 * len(extra_entities)),
                )
            )
            detector_counts["canon.extra_entity"] += 1
            next_index += 1

        md_numbers = extract_numbers(md_text)
        pdf_numbers = extract_numbers(pdf_text)
        if md_numbers and pdf_numbers and md_numbers != pdf_numbers:
            issues.append(
                build_issue(
                    story_id=source.story_id,
                    index=next_index,
                    severity="major",
                    category="canon.numeric_mismatch",
                    page_number=page_number,
                    evidence=f"Numeros distintos MD={sorted(md_numbers)} vs PDF={sorted(pdf_numbers)}.",
                    suggested_action="Confirmar datos numericos con el canon PDF.",
                    source=source_snapshot,
                    detector="numeric_diff_v1",
                    confidence=0.72,
                )
            )
            detector_counts["canon.numeric_mismatch"] += 1
            next_index += 1

        pdf_quotes = extract_quotes(pdf_text)
        if pdf_quotes:
            md_normalized = normalize_for_compare(md_text)
            missing_quotes = []
            for quote in sorted(pdf_quotes, key=lambda value: value.casefold()):
                quote_norm = normalize_for_compare(quote)
                if quote_norm and quote_norm not in md_normalized:
                    missing_quotes.append(quote)
            if missing_quotes:
                issues.append(
                    build_issue(
                        story_id=source.story_id,
                        index=next_index,
                        severity="major",
                        category="canon.quote_loss",
                        page_number=page_number,
                        evidence=f"Fragmentos citados del canon no reflejados: {', '.join(missing_quotes[:3])}.",
                        suggested_action="Revisar fidelidad semantica de frases clave del canon.",
                        source=source_snapshot,
                        detector="quote_presence_v1",
                        confidence=min(1.0, 0.5 + 0.1 * len(missing_quotes)),
                    )
                )
                detector_counts["canon.quote_loss"] += 1
                next_index += 1

        if target_age is not None:
            metrics = age_page_metrics(md_text)
            category, evidence, confidence = detect_age_category(metrics, target_age)
            if category:
                severity = "major" if category == "age.too_complex" else "minor"
                issues.append(
                    build_issue(
                        story_id=source.story_id,
                        index=next_index,
                        severity=severity,
                        category=category,
                        page_number=page_number,
                        evidence=(
                            f"{evidence} avg_sentence={metrics['avg_sentence_length']:.2f}, "
                            f"long_ratio={metrics['long_word_ratio']:.2f}, "
                            f"childish_ratio={metrics['childish_marker_ratio']:.2f}, "
                            f"exclam_ratio={metrics['exclamation_ratio']:.2f}."
                        ),
                        suggested_action="Ajustar tono y complejidad al target_age acordado.",
                        source=source_snapshot,
                        detector="age_balance_v1",
                        confidence=confidence,
                    )
                )
                age_alerts[category] += 1
                detector_counts[category] += 1
                next_index += 1

    for term_key, term_value in sorted(term_evidence_by_key.items()):
        canonical_value = glossary_answer_for(term_value.term, glossary_answers)
        if not canonical_value:
            canonical_value = glossary_answer_for(term_key, glossary_answers)
        if not canonical_value:
            continue
        md_pages_story = sorted(term_value.md_pages_by_story.get(source.story_id, set()))
        if not md_pages_story:
            continue
        canonical_norm = normalize_for_compare(canonical_value)
        mismatching_variants = sorted(
            {
                variant
                for variant in term_value.md_variants
                if normalize_for_compare(variant) and normalize_for_compare(variant) != canonical_norm
            },
            key=lambda value: value.casefold(),
        )
        if not mismatching_variants:
            continue
        page_number = md_pages_story[0]
        md_text = ""
        for page in md_pages:
            if int(page.get("page_number", 0)) == page_number:
                md_text = str(page.get("text_original", ""))
                break
        pdf_text = pdf_pages[page_number - 1] if 1 <= page_number <= len(pdf_pages) else ""
        issues.append(
            build_issue(
                story_id=source.story_id,
                index=next_index,
                severity="major",
                category="canon.term_variant_noncanonical",
                page_number=page_number,
                evidence=(
                    f"Variantes no canonicas detectadas {mismatching_variants[:4]} "
                    f"con canon confirmado '{canonical_value}'."
                ),
                suggested_action="Reemplazar variantes por el termino canonico confirmado.",
                source=build_source_snapshot(
                    md_page=page_number,
                    pdf_page=page_number if 1 <= page_number <= len(pdf_pages) else None,
                    md_text=md_text,
                    pdf_text=pdf_text,
                ),
                detector="glossary_variant_v1",
                confidence=min(1.0, 0.55 + 0.08 * len(mismatching_variants)),
            )
        )
        detector_counts["canon.term_variant_noncanonical"] += 1
        next_index += 1

    overlaps_below = sum(1 for value in overlap_values if value < CANON_OVERLAP_THRESHOLD)
    story_metrics = {
        "page_count_md": len(md_pages),
        "page_count_pdf": len(pdf_pages),
        "overlap_mean": round(fmean(overlap_values), 4) if overlap_values else 0.0,
        "overlap_below_threshold": overlaps_below,
        "ocr_pages_count": len(pdf_data.ocr_pages),
        "age_alerts": age_alerts,
        "detectors": dict(detector_counts),
    }
    return issues, next_index, story_metrics


def build_planned_outputs(sources: list[StorySource], book_rel_path: str) -> list[str]:
    planned_outputs: list[str] = []
    for source in sources:
        planned_outputs.append(f"library/{book_rel_path}/{source.story_id}.json")
        planned_outputs.append(f"library/{book_rel_path}/_reviews/{source.story_id}.issues.json")
    planned_outputs.append(f"library/{book_rel_path}/_reviews/adaptation_context.json")
    return sorted(set(planned_outputs))

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
            "errors": [{"code": "input.missing_inbox", "message": f"No existe inbox: {inbox_dir.as_posix()}"}],
        }

    sources, discovery_errors = discover_story_sources(inbox_dir)
    if discovery_errors:
        return {
            "phase": "failed",
            "pending_questions": [],
            "planned_outputs": [],
            "written_outputs": [],
            "metrics": {},
            "errors": [{"code": "input.discovery_error", "message": message} for message in discovery_errors],
        }
    if not sources:
        return {
            "phase": "failed",
            "pending_questions": [],
            "planned_outputs": [],
            "written_outputs": [],
            "metrics": {},
            "errors": [{"code": "input.empty_batch", "message": "No se encontraron archivos NN.md procesables."}],
        }

    proposed_book_rel = normalize_book_rel(book_rel_path_arg or str(answers.get("book_rel_path", "")).strip())
    if not proposed_book_rel:
        proposed_book_rel = f"cosmere/{slugify(inbox_book_title)}"
    planned_outputs = build_planned_outputs(sources, proposed_book_rel)

    parsed_stories: dict[str, dict[str, Any]] = {}
    markdown_issues_by_story: dict[str, list[tuple[str, str, int | None]]] = {}
    pages_total = 0
    for source in sources:
        parsed_story, parse_issues = parse_story_markdown(source.md_path)
        parsed_stories[source.story_id] = parsed_story
        markdown_issues_by_story[source.story_id] = parse_issues
        pages_total += len(parsed_story.get("pages", []))

    pdf_data_by_story: dict[str, PdfStoryData] = {}
    blocking_errors: list[dict[str, Any]] = []
    parser_backend_counter: Counter[str] = Counter()
    ocr_pages_total = 0

    for source in sources:
        preflight_data, preflight_errors = preflight_story_pdf(source, root_dir)
        if preflight_errors:
            blocking_errors.extend(preflight_errors)
            continue
        assert preflight_data is not None
        pdf_data_by_story[source.story_id] = preflight_data
        parser_backend_counter[preflight_data.backend] += 1
        ocr_pages_total += len(preflight_data.ocr_pages)

    if blocking_errors:
        error_codes = Counter(str(item.get("code", "unknown")) for item in blocking_errors)
        return {
            "phase": "failed",
            "pending_questions": [],
            "planned_outputs": planned_outputs,
            "written_outputs": [],
            "metrics": {
                "stories": len(sources),
                "pages": pages_total,
                "blocking_errors": len(blocking_errors),
                "blocking_errors_by_code": dict(error_codes),
            },
            "errors": blocking_errors,
        }

    glossary_answers_raw = answers.get("glossary", {})
    glossary_answers = glossary_answers_raw if isinstance(glossary_answers_raw, dict) else {}

    term_evidence_by_key = collect_term_evidence(parsed_stories, pdf_data_by_story)
    ambiguous_terms = build_ambiguous_terms(term_evidence_by_key)

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

    for item in ambiguous_terms:
        term = str(item.get("term", "")).strip()
        if not term:
            continue
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
                "reason": str(item.get("reason", "entity_term")),
                "evidence_pages": list(item.get("evidence_pages", [])),
            }
        )

    issues_by_story: dict[str, list[dict[str, Any]]] = {}
    issue_metrics_by_story: dict[str, dict[str, Any]] = {}
    severity_total = {key: 0 for key in SEVERITIES}

    for source in sources:
        story_issues: list[dict[str, Any]] = []
        issue_index = 1
        parsed_story = parsed_stories[source.story_id]

        for severity, category, page_number in markdown_issues_by_story[source.story_id]:
            story_issues.append(
                build_issue(
                    story_id=source.story_id,
                    index=issue_index,
                    severity=severity,
                    category=category,
                    page_number=page_number,
                    evidence=f"Hallazgo estructural en {source.md_path.name}.",
                    suggested_action="Corregir estructura markdown de la propuesta.",
                    detector="markdown_parser_v1",
                    confidence=0.95,
                )
            )
            issue_index += 1

        canonical_issues, issue_index, story_metrics = detect_story_canonical_issues(
            source=source,
            parsed_story=parsed_story,
            pdf_data=pdf_data_by_story[source.story_id],
            start_index=issue_index,
            glossary_answers=glossary_answers,
            target_age=target_age,
            term_evidence_by_key=term_evidence_by_key,
        )
        story_issues.extend(canonical_issues)
        issues_by_story[source.story_id] = story_issues
        issue_metrics_by_story[source.story_id] = story_metrics

        counts = issue_counts(story_issues)
        for key in SEVERITIES:
            severity_total[key] += counts[key]

    metrics = {
        "stories": len(sources),
        "pages": pages_total,
        "issues_total": sum(severity_total.values()),
        "issues_by_severity": severity_total,
        "glossary_terms": len(ambiguous_terms),
        "pending_questions": len(pending_questions),
        "pdf_preflight": {
            "stories_validated": len(pdf_data_by_story),
            "backends": dict(parser_backend_counter),
            "ocr_pages": ocr_pages_total,
        },
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
    context_path = root_dir / "library" / effective_book_rel / "_reviews" / "adaptation_context.json"
    existing_context: dict[str, Any] | None = None
    if context_path.exists():
        try:
            existing_context = load_json_file(context_path)
        except Exception:
            existing_context = None

    canon_sources: list[dict[str, Any]] = []
    for source in sources:
        pdf_data = pdf_data_by_story[source.story_id]
        story_rel = f"{effective_book_rel}/{source.story_id}"
        story_rel_paths.append(story_rel)
        story_file = root_dir / "library" / effective_book_rel / f"{source.story_id}.json"
        issues_file = root_dir / "library" / effective_book_rel / "_reviews" / f"{source.story_id}.issues.json"

        story_payload = build_story_json_payload(
            source=source,
            parsed_story=parsed_stories[source.story_id],
            book_rel_path=effective_book_rel,
            target_age=target_age,
            root_dir=root_dir,
        )
        story_issues = issues_by_story[source.story_id]
        issues_payload = {
            "schema_version": ISSUES_SCHEMA_VERSION,
            "story_id": source.story_id,
            "story_rel_path": story_rel,
            "generated_at": utc_now_iso(),
            "review_mode": "codex_chat_manual",
            "canon_source": {
                "priority": "pdf",
                "reference_pdf_rel_path": pdf_data.pdf_rel_path,
                "backend": pdf_data.backend,
                "ocr_pages": pdf_data.ocr_pages,
            },
            "summary": issue_counts(story_issues),
            "metrics": issue_metrics_by_story.get(source.story_id, {}),
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

        canon_sources.append(
            {
                "story_id": source.story_id,
                "reference_pdf_rel_path": pdf_data.pdf_rel_path,
                "backend": pdf_data.backend,
                "page_count": len(pdf_data.pages_text),
                "ocr_pages": pdf_data.ocr_pages,
            }
        )

    context_payload = merge_context_payload(
        existing=existing_context,
        book_rel_path=effective_book_rel,
        book_title=inbox_book_title,
        target_age=target_age,
        story_rel_paths=story_rel_paths,
        ambiguous_terms=ambiguous_terms,
        glossary_answers=glossary_answers,
        canon_sources=canon_sources,
    )
    if not dry_run:
        write_json_file(context_path, context_payload)
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
        description="Ingesta inicial interactiva con contraste canonico obligatorio NN.md + NN.pdf."
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
            "errors": [{"code": "input.answers_unreadable", "message": f"No se pudo leer answers_json: {exc}"}],
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
