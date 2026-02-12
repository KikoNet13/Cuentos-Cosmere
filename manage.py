from __future__ import annotations

import argparse
import sys

from app import create_app
from app.db import init_schema
from app.importer import (
    export_prompts_backup,
    import_initial_dataset,
    import_prompts_backup,
    migrate_texto_pages,
)


def _print_stats(stats: dict, labels: dict[str, str]) -> None:
    warnings = stats.get("warnings", [])
    for key, value in stats.items():
        if key == "warnings":
            continue
        print(f"{labels.get(key, key)}: {value}")
    for warning in warnings:
        print(f"WARNING: {warning}")


def cmd_init_db() -> None:
    init_schema()
    print("Esquema de base de datos inicializado.")


def cmd_import() -> None:
    try:
        stats = import_initial_dataset()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    print("Importacion completada.")
    labels = {
        "sagas": "Sagas",
        "libros": "Libros",
        "cuentos": "Cuentos",
        "textos": "Textos",
        "referencias_pdf": "Referencias PDF",
        "prompts": "Prompts",
        "imagenes_prompt": "Imagenes de prompt",
        "cuentos_detectados": "Cuentos detectados",
        "textos_importados": "Textos importados",
        "pdf_refs": "Referencias PDF importadas",
        "saga_slug": "Slug de saga",
        "libro_slug": "Slug de libro",
    }
    _print_stats(stats, labels)


def cmd_migrate_texto_pages() -> None:
    stats = migrate_texto_pages()
    print("Migracion de texto a paginas completada.")
    labels = {
        "estado": "Estado",
        "cuentos_migrados": "Cuentos migrados",
        "paginas_migradas": "Paginas migradas",
    }
    _print_stats(stats, labels)


def cmd_export_prompts(path: str | None) -> None:
    stats = export_prompts_backup(path)
    print("Exportacion de prompts completada.")
    labels = {
        "prompts_exportados": "Prompts exportados",
        "ruta": "Archivo generado",
    }
    _print_stats(stats, labels)


def cmd_import_prompts(path: str | None) -> None:
    try:
        stats = import_prompts_backup(path)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    print("Importacion de prompts completada.")
    labels = {
        "prompts_importados": "Prompts importados",
        "imagenes_map": "Mapeos de imagen",
        "prompts_omitidos_bloque_invalido": "Prompts omitidos por bloque invalido",
        "ruta": "Archivo fuente",
    }
    _print_stats(stats, labels)


def cmd_runserver(host: str, port: int, debug: bool) -> None:
    app = create_app()
    app.run(host=host, port=port, debug=debug)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gestor web de Cuentos Cosmere")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Crear esquema de base de datos")
    sub.add_parser("import", help="Importar dataset inicial y escanear archivos locales")
    sub.add_parser("migrate-texto-pages", help="Migrar tabla texto para usar numero_pagina")

    export_prompts = sub.add_parser("export-prompts", help="Exportar prompts desde SQLite a JSON")
    export_prompts.add_argument("--path", default=None, help="Ruta destino del backup JSON")

    import_prompts = sub.add_parser("import-prompts", help="Importar prompts desde JSON a SQLite")
    import_prompts.add_argument("--path", default=None, help="Ruta origen del backup JSON")

    run = sub.add_parser("runserver", help="Ejecutar servidor de desarrollo Flask")
    run.add_argument("--host", default="127.0.0.1", help="Host de escucha")
    run.add_argument("--port", type=int, default=5000, help="Puerto de escucha")
    run.add_argument("--debug", action="store_true", help="Activar modo depuracion")

    args = parser.parse_args()

    if args.command == "init-db":
        cmd_init_db()
    elif args.command == "import":
        cmd_import()
    elif args.command == "migrate-texto-pages":
        cmd_migrate_texto_pages()
    elif args.command == "export-prompts":
        cmd_export_prompts(path=args.path)
    elif args.command == "import-prompts":
        cmd_import_prompts(path=args.path)
    elif args.command == "runserver":
        cmd_runserver(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
