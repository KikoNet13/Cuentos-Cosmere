from __future__ import annotations

import argparse
import sys

from app import create_app
from app.db import init_schema
from app.importer import (
    export_imagenes_backup,
    export_prompts_backup,
    import_initial_dataset,
    import_imagenes_backup,
    import_prompts_backup,
    migrate_models_v3,
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
        "paginas": "Paginas",
        "anclas": "Anclas",
        "versiones_ancla": "Versiones de ancla",
        "imagenes": "Imagenes",
        "requisitos_imagen": "Requisitos de imagen",
        "referencias_pdf": "Referencias PDF",
        "cuentos_detectados": "Cuentos detectados",
        "paginas_importadas": "Paginas importadas",
        "paginas_eliminadas": "Paginas eliminadas",
        "pdf_refs": "Referencias PDF importadas",
        "saga_slug": "Slug de saga",
        "libro_slug": "Slug de libro",
    }
    _print_stats(stats, labels)


def cmd_migrate_texto_pages() -> None:
    stats = migrate_texto_pages()
    print("Migracion legacy completada (alias deprecado).")
    labels = {
        "estado": "Estado",
        "paginas_migradas": "Paginas migradas",
        "prompts_migrados": "Prompts migrados",
        "imagenes_migradas": "Imagenes migradas",
    }
    _print_stats(stats, labels)


def cmd_migrate_models_v3() -> None:
    stats = migrate_models_v3()
    print("Migracion estructural v3 completada.")
    labels = {
        "estado": "Estado",
        "paginas_migradas": "Paginas migradas",
        "prompts_migrados": "Prompts migrados",
        "imagenes_migradas": "Imagenes migradas",
    }
    _print_stats(stats, labels)


def cmd_export_imagenes(path: str | None) -> None:
    stats = export_imagenes_backup(path)
    print("Exportacion de imagenes completada.")
    labels = {
        "imagenes_exportadas": "Imagenes exportadas",
        "ruta": "Archivo generado",
    }
    _print_stats(stats, labels)


def cmd_import_imagenes(path: str | None) -> None:
    try:
        stats = import_imagenes_backup(path)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    print("Importacion de imagenes completada.")
    labels = {
        "imagenes_importadas": "Imagenes importadas",
        "requisitos_importados": "Requisitos importados",
        "imagenes_omitidas": "Imagenes omitidas",
        "ruta": "Archivo generado",
    }
    _print_stats(stats, labels)


def cmd_export_prompts(path: str | None) -> None:
    print("WARNING: export-prompts esta deprecado; usa export-imagenes.")
    stats = export_prompts_backup(path)
    labels = {
        "imagenes_exportadas": "Imagenes exportadas",
        "ruta": "Archivo generado",
    }
    _print_stats(stats, labels)


def cmd_import_prompts(path: str | None) -> None:
    print("WARNING: import-prompts esta deprecado; usa import-imagenes.")
    try:
        stats = import_prompts_backup(path)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    print("Importacion legacy completada.")
    labels = {
        "imagenes_importadas": "Imagenes importadas",
        "requisitos_importados": "Requisitos importados",
        "imagenes_omitidas": "Imagenes omitidas",
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
    sub.add_parser("migrate-models-v3", help="Migrar modelos a Pagina/Ancla/Imagen")

    export_imagenes = sub.add_parser("export-imagenes", help="Exportar imagenes desde SQLite a JSON")
    export_imagenes.add_argument("--path", default=None, help="Ruta destino del backup JSON")

    import_imagenes = sub.add_parser("import-imagenes", help="Importar imagenes desde JSON a SQLite")
    import_imagenes.add_argument("--path", default=None, help="Ruta origen del backup JSON")

    export_prompts = sub.add_parser("export-prompts", help="Alias deprecado de export-imagenes")
    export_prompts.add_argument("--path", default=None, help="Ruta destino del backup JSON")

    import_prompts = sub.add_parser("import-prompts", help="Alias deprecado de import-imagenes")
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
    elif args.command == "migrate-models-v3":
        cmd_migrate_models_v3()
    elif args.command == "export-imagenes":
        cmd_export_imagenes(path=args.path)
    elif args.command == "import-imagenes":
        cmd_import_imagenes(path=args.path)
    elif args.command == "export-prompts":
        cmd_export_prompts(path=args.path)
    elif args.command == "import-prompts":
        cmd_import_prompts(path=args.path)
    elif args.command == "runserver":
        cmd_runserver(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
