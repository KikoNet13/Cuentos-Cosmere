from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _require_pdfium() -> Any:
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'pypdfium2'. Install with: pipenv install pypdfium2"
        ) from exc
    return pdfium


def render_pdf_pages(
    *,
    input_pdf: Path,
    output_dir: Path,
    dpi: int = 160,
    max_pages: int = 0,
) -> tuple[list[Path], int]:
    if not input_pdf.exists() or not input_pdf.is_file():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")
    if dpi <= 0:
        raise ValueError("dpi must be > 0")

    pdfium = _require_pdfium()
    output_dir.mkdir(parents=True, exist_ok=True)

    document = pdfium.PdfDocument(str(input_pdf))
    total_pages = len(document)
    target_pages = total_pages if max_pages <= 0 else min(max_pages, total_pages)
    scale = float(dpi) / 72.0

    written: list[Path] = []
    for idx in range(target_pages):
        page = document[idx]
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        output_path = output_dir / f"page-{idx + 1:03d}.png"
        pil_image.save(output_path, format="PNG")
        written.append(output_path)

        pil_image.close()
        if hasattr(bitmap, "close"):
            bitmap.close()
        if hasattr(page, "close"):
            page.close()

    if hasattr(document, "close"):
        document.close()
    return written, total_pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG using pypdfium2")
    parser.add_argument("--input", required=True, help="Input PDF path")
    parser.add_argument("--output-dir", required=True, help="Output directory for PNG pages")
    parser.add_argument("--dpi", type=int, default=160, help="Render DPI")
    parser.add_argument("--max-pages", type=int, default=0, help="Max pages to render (0=all)")
    args = parser.parse_args()

    input_pdf = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    try:
        written, total_pages = render_pdf_pages(
            input_pdf=input_pdf,
            output_dir=output_dir,
            dpi=int(args.dpi),
            max_pages=int(args.max_pages),
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"input_pdf: {input_pdf}")
    print(f"output_dir: {output_dir}")
    print(f"total_pages: {total_pages}")
    print(f"rendered_pages: {len(written)}")
    if written:
        print(f"first_page: {written[0]}")
        print(f"last_page: {written[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
