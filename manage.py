from __future__ import annotations

import argparse
import sys

from app.config import APP_TITLE


def cmd_runserver(host: str, port: int, debug: bool) -> None:
    from app import create_app

    app = create_app()
    app.run(host=host, port=port, debug=debug)


def _print_pdf_validation(validation: dict[str, object]) -> None:
    story_rel = str(validation.get("story_rel_path", ""))
    story_id = str(validation.get("story_id", ""))
    title = str(validation.get("title", ""))
    page_count = int(validation.get("page_count", 0) or 0)
    is_valid = bool(validation.get("is_valid", False))

    print(f"story_rel_path: {story_rel}")
    print(f"story_id: {story_id}")
    print(f"title: {title}")
    print(f"page_count: {page_count}")
    if is_valid:
        print("validation: OK")
        return

    print("validation: ERROR")
    errors = validation.get("errors", [])
    if not isinstance(errors, list):
        return
    for idx, error in enumerate(errors, start=1):
        if not isinstance(error, dict):
            continue
        code = str(error.get("code", "error"))
        slot_name = str(error.get("slot_name", "slot"))
        page_number = error.get("page_number", None)
        location = f"pagina {page_number}" if isinstance(page_number, int) else "portada"
        message = str(error.get("message", "")).strip() or code
        print(f"  {idx}. [{code}] {location}::{slot_name} - {message}")


def cmd_export_story_pdf(
    *,
    story: str,
    output: str | None,
    size_cm: float,
    dry_run: bool,
    overwrite: bool,
) -> int:
    from app.pdf_export import PdfExportError, export_story_pdf, validate_story_for_pdf
    from app.story_store import StoryStoreError

    try:
        validation = validate_story_for_pdf(story_rel_path=story)
    except (FileNotFoundError, StoryStoreError, PdfExportError) as exc:
        print(f"ERROR: {exc}")
        return 1

    _print_pdf_validation(validation)
    if dry_run:
        return 0 if bool(validation.get("is_valid", False)) else 1

    if not bool(validation.get("is_valid", False)):
        return 1

    try:
        result = export_story_pdf(
            story_rel_path=story,
            output_path=output,
            size_cm=size_cm,
            overwrite=overwrite,
        )
    except (FileNotFoundError, StoryStoreError, PdfExportError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print("export: OK")
    print(f"output_path: {result['output_path']}")
    print(f"spread_count: {result['spread_count']}")
    print(f"size_cm: {result['size_cm']}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("runserver", help="Ejecutar servidor de desarrollo Flask")
    run.add_argument("--host", default="127.0.0.1", help="Host de escucha")
    run.add_argument("--port", type=int, default=5000, help="Puerto de escucha")
    run.add_argument("--debug", action="store_true", help="Activar modo depuracion")

    export = sub.add_parser("export-story-pdf", help="Exportar cuento maquetado a PDF")
    export.add_argument("--story", required=True, help="Ruta de cuento, por ejemplo: los_juegos_del_hambre/01")
    export.add_argument("--output", default=None, help="Ruta de salida del PDF")
    export.add_argument("--size-cm", type=float, default=20.0, help="Tamano base en cm de cada pagina cuadrada")
    export.add_argument("--dry-run", action="store_true", help="Validar cuento sin generar PDF")
    export.add_argument("--overwrite", action="store_true", help="Permitir sobreescritura del archivo destino")

    args = parser.parse_args()

    if args.command == "runserver":
        cmd_runserver(host=args.host, port=args.port, debug=args.debug)
    elif args.command == "export-story-pdf":
        exit_code = cmd_export_story_pdf(
            story=args.story,
            output=args.output,
            size_cm=args.size_cm,
            dry_run=args.dry_run,
            overwrite=args.overwrite,
        )
        if exit_code != 0:
            sys.exit(exit_code)
    else:
        print(f"ERROR: comando no soportado: {args.command}")
        sys.exit(2)


if __name__ == "__main__":
    main()
