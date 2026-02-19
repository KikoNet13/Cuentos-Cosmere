from __future__ import annotations

import io
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


def _require_reportlab() -> tuple[Any, Any, Any, Any, Any]:
    try:
        from reportlab.lib import colors
        from reportlab.lib.units import cm as rl_cm
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError as exc:
        raise PdfExportError(
            "Falta dependencia 'reportlab'. Instala con: pipenv install reportlab"
        ) from exc
    return rl_canvas, pdfmetrics, ImageReader, colors, rl_cm


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


def _wrap_line_to_width(text: str, *, pdfmetrics_mod: Any, font_name: str, font_size: float, max_width: float) -> list[str]:
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


def _wrap_text(text: str, *, pdfmetrics_mod: Any, font_name: str, font_size: float, max_width: float) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = normalized.split("\n")
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
    for font_size in (12.0, 11.5, 11.0, 10.5, 10.0):
        line_height = font_size * 1.35
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


def _draw_title_block(
    *,
    canvas_obj: Any,
    pdfmetrics_mod: Any,
    title: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    for font_size in (28.0, 26.0, 24.0, 22.0, 20.0, 18.0, 16.0):
        lines = _wrap_text(
            title,
            pdfmetrics_mod=pdfmetrics_mod,
            font_name="Helvetica-Bold",
            font_size=font_size,
            max_width=width,
        )
        line_height = font_size * 1.2
        needed_height = len(lines) * line_height
        if needed_height > height:
            continue

        cursor_y = y + height - font_size
        canvas_obj.setFont("Helvetica-Bold", font_size)
        for line in lines:
            canvas_obj.drawString(x, cursor_y, line)
            cursor_y -= line_height
        return

    raise PdfExportError("text_overflow: la portada no puede renderizar el titulo en el panel izquierdo.")


def _draw_cover_spread(
    *,
    canvas_obj: Any,
    payload: dict[str, Any],
    cover_image_path: Path,
    spread_w: float,
    spread_h: float,
    image_reader_cls: Any,
    colors_mod: Any,
    pdfmetrics_mod: Any,
) -> None:
    panel_w = spread_w / 2.0
    margin = 34.0

    canvas_obj.setFillColor(colors_mod.HexColor("#F7F2E8"))
    canvas_obj.rect(0, 0, panel_w, spread_h, fill=1, stroke=0)

    canvas_obj.setFillColor(colors_mod.HexColor("#1F1F1F"))
    canvas_obj.setFont("Helvetica-Bold", 16)
    canvas_obj.drawString(margin, spread_h - margin, "Cuento ilustrado")

    title = str(payload.get("title", "")).strip() or "Sin titulo"
    _draw_title_block(
        canvas_obj=canvas_obj,
        pdfmetrics_mod=pdfmetrics_mod,
        title=title,
        x=margin,
        y=spread_h * 0.34,
        width=panel_w - (margin * 2),
        height=spread_h * 0.42,
    )

    story_id = str(payload.get("story_id", "")).strip() or "--"
    page_count = len(_sorted_pages(payload))
    book_rel_path = _normalize_rel_path(str(payload.get("book_rel_path", ""))) or "library"

    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.drawString(margin, margin + 34, f"Cuento {story_id}")
    canvas_obj.drawString(margin, margin + 18, f"Paginas: {page_count}")
    canvas_obj.drawString(margin, margin + 2, f"Saga: {book_rel_path}")

    _draw_image_fill(
        canvas_obj=canvas_obj,
        image_reader_cls=image_reader_cls,
        image_path=cover_image_path,
        x=panel_w,
        y=0.0,
        width=panel_w,
        height=spread_h,
    )


def _draw_story_spread(
    *,
    canvas_obj: Any,
    page: dict[str, Any],
    main_path: Path,
    secondary_path: Path | None,
    spread_w: float,
    spread_h: float,
    image_reader_cls: Any,
    pdfmetrics_mod: Any,
    colors_mod: Any,
) -> None:
    panel_w = spread_w / 2.0
    margin = 22.0

    canvas_obj.setFillColor(colors_mod.white)
    canvas_obj.rect(0, 0, panel_w, spread_h, fill=1, stroke=0)
    canvas_obj.setStrokeColor(colors_mod.HexColor("#E5E5E5"))
    canvas_obj.setLineWidth(0.8)
    canvas_obj.line(panel_w, 0, panel_w, spread_h)

    page_number = int(page.get("page_number", 0))
    canvas_obj.setFillColor(colors_mod.HexColor("#1F1F1F"))
    canvas_obj.setFont("Helvetica-Bold", 13)
    canvas_obj.drawString(margin, spread_h - margin, f"Pagina {page_number}")

    text_x = margin
    text_y = margin
    text_w = panel_w - (margin * 2)
    text_h = spread_h - (margin * 2) - 20

    if secondary_path is not None:
        thumb_w = min(text_w * 0.38, panel_w * 0.36)
        thumb_h = thumb_w
        thumb_x = panel_w - margin - thumb_w
        thumb_y = margin

        _draw_image_fill(
            canvas_obj=canvas_obj,
            image_reader_cls=image_reader_cls,
            image_path=secondary_path,
            x=thumb_x,
            y=thumb_y,
            width=thumb_w,
            height=thumb_h,
        )
        canvas_obj.setStrokeColor(colors_mod.HexColor("#BDBDBD"))
        canvas_obj.setLineWidth(0.8)
        canvas_obj.rect(thumb_x, thumb_y, thumb_w, thumb_h, fill=0, stroke=1)
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.setFillColor(colors_mod.HexColor("#4A4A4A"))
        canvas_obj.drawString(thumb_x + 4, thumb_y + thumb_h + 3, "Sec.")

        reserved_h = thumb_h + 16
        text_y += reserved_h
        text_h -= reserved_h

    fit = _fit_text_block(
        text=str(page.get("text", "")),
        pdfmetrics_mod=pdfmetrics_mod,
        font_name="Helvetica",
        max_width=text_w,
        max_height=text_h,
    )
    if fit is None:
        raise PdfExportError(
            f"text_overflow: la pagina {page_number} excede el area de texto "
            "incluso reduciendo de 12pt a 10pt."
        )

    font_size, line_height, lines = fit
    cursor_y = text_y + text_h - font_size
    canvas_obj.setFillColor(colors_mod.HexColor("#262626"))
    canvas_obj.setFont("Helvetica", font_size)
    for line in lines:
        canvas_obj.drawString(text_x, cursor_y, line)
        cursor_y -= line_height

    _draw_image_fill(
        canvas_obj=canvas_obj,
        image_reader_cls=image_reader_cls,
        image_path=main_path,
        x=panel_w,
        y=0.0,
        width=panel_w,
        height=spread_h,
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

        secondary_path: Path | None = None
        secondary_slot = images.get("secondary")
        if isinstance(secondary_slot, dict) and slot_state(secondary_slot) == SLOT_STATE_COMPLETED:
            secondary_path = resolve_active_asset_path(secondary_slot)

        page_rows.append(
            {
                "page": page,
                "main_path": main_path,
                "secondary_path": secondary_path,
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

    rl_canvas, pdfmetrics_mod, image_reader_cls, colors_mod, rl_cm = _require_reportlab()
    spread_w = 2.0 * float(size_cm) * rl_cm
    spread_h = float(size_cm) * rl_cm
    canvas_obj = rl_canvas.Canvas(str(output), pagesize=(spread_w, spread_h))

    _draw_cover_spread(
        canvas_obj=canvas_obj,
        payload=payload,
        cover_image_path=cover_path,
        spread_w=spread_w,
        spread_h=spread_h,
        image_reader_cls=image_reader_cls,
        colors_mod=colors_mod,
        pdfmetrics_mod=pdfmetrics_mod,
    )

    for row in active_paths.get("pages", []):
        if not isinstance(row, dict):
            continue
        page = row.get("page")
        main_path = row.get("main_path")
        secondary_path = row.get("secondary_path")
        if not isinstance(page, dict) or not isinstance(main_path, Path):
            continue

        canvas_obj.showPage()
        _draw_story_spread(
            canvas_obj=canvas_obj,
            page=page,
            main_path=main_path,
            secondary_path=secondary_path if isinstance(secondary_path, Path) else None,
            spread_w=spread_w,
            spread_h=spread_h,
            image_reader_cls=image_reader_cls,
            pdfmetrics_mod=pdfmetrics_mod,
            colors_mod=colors_mod,
        )

    canvas_obj.save()

    return {
        "story_rel_path": validation["story_rel_path"],
        "story_id": validation["story_id"],
        "output_path": str(output),
        "spread_count": len(active_paths.get("pages", [])) + 1,
        "size_cm": float(size_cm),
    }
