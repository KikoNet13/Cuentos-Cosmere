from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any

from PIL import Image

from .config import LIBRARY_ROOT, ROOT_DIR
from .story_progress import (
    SLOT_STATE_COMPLETED,
    SLOT_STATE_NOT_REQUIRED,
    SLOT_STATE_NO_PROMPT,
    SLOT_STATE_PENDING,
    resolve_active_asset_path,
    slot_state,
)
from .story_store import load_story


class PdfExportError(RuntimeError):
    pass


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _sorted_pages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    pages = payload.get("pages", [])
    if not isinstance(pages, list):
        return []
    return sorted(
        [item for item in pages if isinstance(item, dict)],
        key=lambda item: int(item.get("page_number", 0)),
    )


def _build_validation_error(
    *,
    code: str,
    item_type: str,
    slot_name: str,
    page_number: int | None,
    state: str,
    message: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "item_type": item_type,
        "slot_name": slot_name,
        "page_number": page_number,
        "state": state,
        "message": message,
    }


def _validate_required_slot(
    *,
    slot_payload: dict[str, Any] | None,
    item_type: str,
    slot_name: str,
    page_number: int | None,
) -> list[dict[str, Any]]:
    if not isinstance(slot_payload, dict):
        return [
            _build_validation_error(
                code="slot_missing",
                item_type=item_type,
                slot_name=slot_name,
                page_number=page_number,
                state="missing",
                message=f"Falta slot requerido: {slot_name}.",
            )
        ]

    state = slot_state(slot_payload)
    if state == SLOT_STATE_NOT_REQUIRED:
        return [
            _build_validation_error(
                code="slot_not_required",
                item_type=item_type,
                slot_name=slot_name,
                page_number=page_number,
                state=state,
                message=f"El slot requerido {slot_name} no puede estar en not_required.",
            )
        ]
    if state == SLOT_STATE_NO_PROMPT:
        return [
            _build_validation_error(
                code="slot_no_prompt",
                item_type=item_type,
                slot_name=slot_name,
                page_number=page_number,
                state=state,
                message=f"El slot requerido {slot_name} no tiene prompt.",
            )
        ]
    if state == SLOT_STATE_PENDING:
        return [
            _build_validation_error(
                code="slot_pending",
                item_type=item_type,
                slot_name=slot_name,
                page_number=page_number,
                state=state,
                message=f"El slot requerido {slot_name} no tiene imagen activa valida.",
            )
        ]
    if state != SLOT_STATE_COMPLETED:
        return [
            _build_validation_error(
                code="slot_unknown_state",
                item_type=item_type,
                slot_name=slot_name,
                page_number=page_number,
                state=state,
                message=f"Estado inesperado para {slot_name}: {state}",
            )
        ]
    return []


def _validate_secondary_slot(
    *,
    slot_payload: dict[str, Any] | None,
    page_number: int,
) -> list[dict[str, Any]]:
    if not isinstance(slot_payload, dict):
        return []

    state = slot_state(slot_payload)
    if state in {SLOT_STATE_NOT_REQUIRED, SLOT_STATE_NO_PROMPT, SLOT_STATE_COMPLETED}:
        return []
    if state == SLOT_STATE_PENDING:
        return [
            _build_validation_error(
                code="secondary_pending",
                item_type="slot",
                slot_name="secondary",
                page_number=page_number,
                state=state,
                message="El slot secondary tiene prompt pero no imagen activa valida.",
            )
        ]
    return [
        _build_validation_error(
            code="secondary_unknown_state",
            item_type="slot",
            slot_name="secondary",
            page_number=page_number,
            state=state,
            message=f"Estado inesperado para secondary: {state}",
        )
    ]


def validate_story_for_pdf(*, story_rel_path: str) -> dict[str, Any]:
    normalized_story = _normalize_rel_path(story_rel_path)
    payload = load_story(normalized_story)

    errors: list[dict[str, Any]] = []

    cover = payload.get("cover")
    errors.extend(
        _validate_required_slot(
            slot_payload=cover if isinstance(cover, dict) else None,
            item_type="cover",
            slot_name="cover",
            page_number=None,
        )
    )

    for page in _sorted_pages(payload):
        try:
            page_number = int(page.get("page_number", 0))
        except (TypeError, ValueError):
            page_number = 0
        if page_number <= 0:
            errors.append(
                _build_validation_error(
                    code="page_number_invalid",
                    item_type="slot",
                    slot_name="main",
                    page_number=None,
                    state="invalid",
                    message="Se encontro una pagina con page_number invalido.",
                )
            )
            continue

        images = page.get("images", {})
        if not isinstance(images, dict):
            images = {}

        main_slot = images.get("main")
        errors.extend(
            _validate_required_slot(
                slot_payload=main_slot if isinstance(main_slot, dict) else None,
                item_type="slot",
                slot_name="main",
                page_number=page_number,
            )
        )

        secondary_slot = images.get("secondary")
        errors.extend(
            _validate_secondary_slot(
                slot_payload=secondary_slot if isinstance(secondary_slot, dict) else None,
                page_number=page_number,
            )
        )

    return {
        "story_rel_path": normalized_story,
        "story_id": str(payload.get("story_id", "")).strip(),
        "title": str(payload.get("title", "")).strip(),
        "book_rel_path": _normalize_rel_path(str(payload.get("book_rel_path", ""))),
        "page_count": len(_sorted_pages(payload)),
        "is_valid": not errors,
        "errors": errors,
    }


def _require_reportlab() -> tuple[Any, Any, Any, Any, Any, Any]:
    try:
        from reportlab.lib import colors
        from reportlab.lib.units import cm as rl_cm
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError as exc:
        raise PdfExportError(
            "Falta dependencia 'reportlab'. Instala con: pipenv install reportlab"
        ) from exc
    return rl_canvas, pdfmetrics, ImageReader, colors, rl_cm, TTFont


def _default_output_path(payload: dict[str, Any]) -> Path:
    story_id = str(payload.get("story_id", "")).strip() or "00"
    book_rel_path = _normalize_rel_path(str(payload.get("book_rel_path", "")))
    if book_rel_path:
        return LIBRARY_ROOT / book_rel_path / f"{story_id}.pdf"
    return LIBRARY_ROOT / f"{story_id}.pdf"


def _resolve_output_path(output_path: str | Path | None, payload: dict[str, Any]) -> Path:
    if output_path is None:
        return _default_output_path(payload).resolve()

    raw = Path(output_path).expanduser()
    if raw.is_absolute():
        return raw.resolve()
    return (ROOT_DIR / raw).resolve()


def _register_font_from_candidates(
    *,
    pdfmetrics_mod: Any,
    ttfont_cls: Any,
    font_name: str,
    paths: list[str],
) -> str | None:
    for raw_path in paths:
        candidate = Path(raw_path)
        if not candidate.exists():
            continue
        try:
            pdfmetrics_mod.registerFont(ttfont_cls(font_name, str(candidate)))
            return font_name
        except Exception:
            continue
    return None


def _resolve_pdf_fonts(*, pdfmetrics_mod: Any, ttfont_cls: Any) -> dict[str, str]:
    families = [
        (
            "StoryGeorgia",
            [r"C:\Windows\Fonts\georgia.ttf"],
            [r"C:\Windows\Fonts\georgiab.ttf"],
        ),
        (
            "StoryCambria",
            [r"C:\Windows\Fonts\cambria.ttf", r"C:\Windows\Fonts\cambria.ttc"],
            [r"C:\Windows\Fonts\cambriab.ttf"],
        ),
    ]

    for prefix, regular_paths, bold_paths in families:
        regular_name = f"{prefix}-Regular"
        bold_name = f"{prefix}-Bold"
        regular_ok = _register_font_from_candidates(
            pdfmetrics_mod=pdfmetrics_mod,
            ttfont_cls=ttfont_cls,
            font_name=regular_name,
            paths=regular_paths,
        )
        bold_ok = _register_font_from_candidates(
            pdfmetrics_mod=pdfmetrics_mod,
            ttfont_cls=ttfont_cls,
            font_name=bold_name,
            paths=bold_paths,
        )
        if regular_ok and bold_ok:
            return {"regular": regular_name, "bold": bold_name}

    return {"regular": "Times-Roman", "bold": "Times-Bold"}


def _split_long_paragraph(paragraph: str, *, max_chars: int = 220) -> list[str]:
    clean = re.sub(r"\s+", " ", paragraph).strip()
    if not clean:
        return []
    if len(clean) <= max_chars:
        return [clean]

    sentences = re.split(r"(?<=[.!?])\s+", clean)
    if len(sentences) <= 1:
        return [clean]

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        candidate = sentence if not current else f"{current} {sentence}"
        if len(candidate) <= max_chars or not current:
            current = candidate
            continue
        chunks.append(current)
        current = sentence

    if current:
        chunks.append(current)
    return chunks or [clean]


def _normalize_story_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return ""

    base_paragraphs = [line.strip() for line in normalized.split("\n")]
    base_paragraphs = [line for line in base_paragraphs if line]
    if not base_paragraphs:
        return ""

    polished: list[str] = []
    for paragraph in base_paragraphs:
        split_dialogue = re.sub(r"(?<!\n)\s*(—)(?=[A-ZÁÉÍÓÚÑ¡¿])", r"\n\1", paragraph)
        split_dialogue = re.sub(r"(?<!\n)\s*(«)", r"\n\1", split_dialogue)

        for chunk in split_dialogue.split("\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            polished.extend(_split_long_paragraph(chunk, max_chars=220))

    return "\n\n".join(polished)


def _wrap_line_to_width(
    text: str,
    *,
    pdfmetrics_mod: Any,
    font_name: str,
    font_size: float,
    max_width: float,
) -> list[str]:
    if not text:
        return [""]

    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]

    def split_word(word: str) -> list[str]:
        chunks: list[str] = []
        chunk = ""
        for char in word:
            candidate = f"{chunk}{char}"
            if pdfmetrics_mod.stringWidth(candidate, font_name, font_size) <= max_width:
                chunk = candidate
                continue
            if chunk:
                chunks.append(chunk)
            chunk = char
        if chunk:
            chunks.append(chunk)
        return chunks or [word]

    if pdfmetrics_mod.stringWidth(current, font_name, font_size) > max_width:
        broken = split_word(current)
        lines.extend(broken[:-1])
        current = broken[-1]

    for word in words[1:]:
        candidate = f"{current} {word}"
        if pdfmetrics_mod.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
            continue

        lines.append(current)
        current = word
        if pdfmetrics_mod.stringWidth(current, font_name, font_size) > max_width:
            broken = split_word(current)
            lines.extend(broken[:-1])
            current = broken[-1]

    lines.append(current)
    return lines


def _wrap_text(
    text: str,
    *,
    pdfmetrics_mod: Any,
    font_name: str,
    font_size: float,
    max_width: float,
) -> list[str]:
    paragraphs = text.split("\n")
    lines: list[str] = []
    for index, paragraph in enumerate(paragraphs):
        wrapped = _wrap_line_to_width(
            paragraph,
            pdfmetrics_mod=pdfmetrics_mod,
            font_name=font_name,
            font_size=font_size,
            max_width=max_width,
        )
        lines.extend(wrapped)
        if index < len(paragraphs) - 1:
            lines.append("")
    return lines


def _fit_text_block(
    *,
    text: str,
    pdfmetrics_mod: Any,
    font_name: str,
    max_width: float,
    max_height: float,
) -> tuple[float, float, list[str]] | None:
    for font_size in (18.0, 17.5, 17.0, 16.5, 16.0, 15.5, 15.0, 14.5, 14.0):
        line_height = font_size * 1.52
        lines = _wrap_text(
            text,
            pdfmetrics_mod=pdfmetrics_mod,
            font_name=font_name,
            font_size=font_size,
            max_width=max_width,
        )
        needed_height = len(lines) * line_height
        if needed_height <= max_height:
            return font_size, line_height, lines
    return None


def _draw_image_fill(
    *,
    canvas_obj: Any,
    image_reader_cls: Any,
    image_path: Path,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    with Image.open(image_path) as source:
        img = source.convert("RGBA")
        src_w, src_h = img.size
        src_ratio = src_w / src_h if src_h else 1.0
        target_ratio = width / height if height else 1.0

        if src_ratio > target_ratio:
            new_w = max(1, int(src_h * target_ratio))
            offset_x = max(0, (src_w - new_w) // 2)
            box = (offset_x, 0, offset_x + new_w, src_h)
        else:
            new_h = max(1, int(src_w / target_ratio))
            offset_y = max(0, (src_h - new_h) // 2)
            box = (0, offset_y, src_w, offset_y + new_h)

        cropped = img.crop(box)
        rgb = Image.new("RGB", cropped.size, (255, 255, 255))
        rgb.paste(cropped, mask=cropped.split()[-1])

        buffer = io.BytesIO()
        rgb.save(buffer, format="PNG")
        buffer.seek(0)
        reader = image_reader_cls(buffer)
        canvas_obj.drawImage(
            reader,
            x,
            y,
            width=width,
            height=height,
            preserveAspectRatio=False,
            mask="auto",
        )


def _draw_centered_title(
    *,
    canvas_obj: Any,
    pdfmetrics_mod: Any,
    title: str,
    font_name: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    for font_size in (44.0, 40.0, 36.0, 32.0, 28.0, 24.0):
        lines = _wrap_text(
            title,
            pdfmetrics_mod=pdfmetrics_mod,
            font_name=font_name,
            font_size=font_size,
            max_width=width,
        )
        lines = [line for line in lines if line.strip()]
        if not lines:
            continue
        line_height = font_size * 1.18
        needed_height = len(lines) * line_height
        if needed_height > height:
            continue

        start_y = y + ((height - needed_height) / 2.0) + needed_height - font_size
        canvas_obj.setFont(font_name, font_size)
        for index, line in enumerate(lines):
            line_width = pdfmetrics_mod.stringWidth(line, font_name, font_size)
            line_x = x + max(0.0, (width - line_width) / 2.0)
            line_y = start_y - (index * line_height)
            canvas_obj.drawString(line_x, line_y, line)
        return

    raise PdfExportError("text_overflow: la portada no puede renderizar el titulo en la banda superior.")


def _draw_cover_page(
    *,
    canvas_obj: Any,
    payload: dict[str, Any],
    cover_image_path: Path,
    page_size: float,
    image_reader_cls: Any,
    colors_mod: Any,
    pdfmetrics_mod: Any,
    fonts: dict[str, str],
) -> None:
    _draw_image_fill(
        canvas_obj=canvas_obj,
        image_reader_cls=image_reader_cls,
        image_path=cover_image_path,
        x=0.0,
        y=0.0,
        width=page_size,
        height=page_size,
    )

    band_h = page_size * 0.2
    band_y = page_size - band_h
    canvas_obj.saveState()
    canvas_obj.setFillColor(colors_mod.HexColor("#151515"))
    if hasattr(canvas_obj, "setFillAlpha"):
        canvas_obj.setFillAlpha(0.48)
    canvas_obj.rect(0.0, band_y, page_size, band_h, fill=1, stroke=0)
    canvas_obj.restoreState()

    title = str(payload.get("title", "")).strip() or "Sin titulo"
    canvas_obj.setFillColor(colors_mod.white)
    _draw_centered_title(
        canvas_obj=canvas_obj,
        pdfmetrics_mod=pdfmetrics_mod,
        title=title,
        font_name=fonts["bold"],
        x=24.0,
        y=band_y + 8.0,
        width=page_size - 48.0,
        height=band_h - 16.0,
    )


def _draw_text_page(
    *,
    canvas_obj: Any,
    page: dict[str, Any],
    page_size: float,
    pdfmetrics_mod: Any,
    colors_mod: Any,
    fonts: dict[str, str],
) -> None:
    margin = max(36.0, page_size * 0.075)
    header_gap = 30.0

    canvas_obj.setFillColor(colors_mod.white)
    canvas_obj.rect(0.0, 0.0, page_size, page_size, fill=1, stroke=0)

    page_number = int(page.get("page_number", 0))
    canvas_obj.setFillColor(colors_mod.HexColor("#2A2A2A"))
    canvas_obj.setFont(fonts["bold"], 14.0)
    canvas_obj.drawString(margin, page_size - margin, f"Pagina {page_number}")

    text_x = margin
    text_y = margin
    text_w = page_size - (margin * 2.0)
    text_h = page_size - (margin * 2.0) - header_gap
    story_text = _normalize_story_text(str(page.get("text", "")))

    fit = _fit_text_block(
        text=story_text,
        pdfmetrics_mod=pdfmetrics_mod,
        font_name=fonts["regular"],
        max_width=text_w,
        max_height=text_h,
    )
    if fit is None:
        raise PdfExportError(
            f"text_overflow: la pagina {page_number} excede el area de texto "
            "incluso reduciendo de 18pt a 14pt."
        )

    font_size, line_height, lines = fit
    cursor_y = text_y + text_h - font_size
    canvas_obj.setFillColor(colors_mod.HexColor("#1F1F1F"))
    canvas_obj.setFont(fonts["regular"], font_size)
    for line in lines:
        if line:
            canvas_obj.drawString(text_x, cursor_y, line)
        cursor_y -= line_height


def _draw_image_page(
    *,
    canvas_obj: Any,
    main_path: Path,
    page_size: float,
    image_reader_cls: Any,
) -> None:
    _draw_image_fill(
        canvas_obj=canvas_obj,
        image_reader_cls=image_reader_cls,
        image_path=main_path,
        x=0.0,
        y=0.0,
        width=page_size,
        height=page_size,
    )


def _collect_active_paths(payload: dict[str, Any]) -> dict[str, Any]:
    cover = payload.get("cover", {})
    cover_path = resolve_active_asset_path(cover if isinstance(cover, dict) else {})

    page_rows: list[dict[str, Any]] = []
    for page in _sorted_pages(payload):
        images = page.get("images", {})
        if not isinstance(images, dict):
            images = {}

        main_slot = images.get("main", {})
        if not isinstance(main_slot, dict):
            main_slot = {}
        main_path = resolve_active_asset_path(main_slot)

        page_rows.append(
            {
                "page": page,
                "main_path": main_path,
            }
        )

    return {
        "cover_path": cover_path,
        "pages": page_rows,
    }


def format_validation_errors(validation: dict[str, Any]) -> str:
    errors = validation.get("errors", [])
    if not isinstance(errors, list) or not errors:
        return "Sin errores."

    lines = []
    for idx, error in enumerate(errors, start=1):
        if not isinstance(error, dict):
            continue
        code = str(error.get("code", "error"))
        slot_name = str(error.get("slot_name", "slot"))
        page_number = error.get("page_number", None)
        location = f"pagina {page_number}" if isinstance(page_number, int) else "portada"
        message = str(error.get("message", "")).strip() or code
        lines.append(f"{idx}. [{code}] {location}::{slot_name} - {message}")
    return "\n".join(lines)


def export_story_pdf(
    *,
    story_rel_path: str,
    output_path: str | Path | None = None,
    size_cm: float = 20.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    if size_cm <= 0:
        raise PdfExportError("size_cm debe ser mayor que 0.")

    validation = validate_story_for_pdf(story_rel_path=story_rel_path)
    if not validation.get("is_valid", False):
        raise PdfExportError(
            "El cuento no esta listo para exportacion PDF:\n" + format_validation_errors(validation)
        )

    payload = load_story(validation["story_rel_path"])
    active_paths = _collect_active_paths(payload)
    cover_path = active_paths.get("cover_path")
    if not isinstance(cover_path, Path) or not cover_path.exists():
        raise PdfExportError("No se pudo resolver la imagen activa de portada para exportar.")

    for row in active_paths.get("pages", []):
        if not isinstance(row, dict):
            continue
        page = row.get("page", {})
        page_number = int(page.get("page_number", 0)) if isinstance(page, dict) else 0
        main_path = row.get("main_path")
        if not isinstance(main_path, Path) or not main_path.exists():
            raise PdfExportError(f"No se pudo resolver la imagen activa main de la pagina {page_number}.")

    output = _resolve_output_path(output_path, payload)
    if output.exists() and not overwrite:
        raise PdfExportError(f"El archivo ya existe: {output}. Usa --overwrite para reemplazarlo.")

    output.parent.mkdir(parents=True, exist_ok=True)

    rl_canvas, pdfmetrics_mod, image_reader_cls, colors_mod, rl_cm, ttfont_cls = _require_reportlab()
    fonts = _resolve_pdf_fonts(pdfmetrics_mod=pdfmetrics_mod, ttfont_cls=ttfont_cls)

    page_size = float(size_cm) * rl_cm
    canvas_obj = rl_canvas.Canvas(str(output), pagesize=(page_size, page_size))

    _draw_cover_page(
        canvas_obj=canvas_obj,
        payload=payload,
        cover_image_path=cover_path,
        page_size=page_size,
        image_reader_cls=image_reader_cls,
        colors_mod=colors_mod,
        pdfmetrics_mod=pdfmetrics_mod,
        fonts=fonts,
    )

    for row in active_paths.get("pages", []):
        if not isinstance(row, dict):
            continue
        page = row.get("page")
        main_path = row.get("main_path")
        if not isinstance(page, dict) or not isinstance(main_path, Path):
            continue

        canvas_obj.showPage()
        _draw_text_page(
            canvas_obj=canvas_obj,
            page=page,
            page_size=page_size,
            pdfmetrics_mod=pdfmetrics_mod,
            colors_mod=colors_mod,
            fonts=fonts,
        )

        canvas_obj.showPage()
        _draw_image_page(
            canvas_obj=canvas_obj,
            main_path=main_path,
            page_size=page_size,
            image_reader_cls=image_reader_cls,
        )

    canvas_obj.save()

    page_count = 1 + (len(active_paths.get("pages", [])) * 2)
    return {
        "story_rel_path": validation["story_rel_path"],
        "story_id": validation["story_id"],
        "output_path": str(output),
        "layout_mode": "paged",
        "page_count": page_count,
        "spread_count": page_count,
        "size_cm": float(size_cm),
    }
