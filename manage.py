from __future__ import annotations

import argparse
import sys

def _print_stats(stats: dict, labels: dict[str, str]) -> None:
    warnings = stats.get("warnings", [])
    for key, value in stats.items():
        if key == "warnings":
            continue
        print(f"{labels.get(key, key)}: {value}")
    for warning in warnings:
        print(f"WARNING: {warning}")


def cmd_init_db() -> None:
    from app.db import init_schema

    init_schema()
    print("Esquema de base de datos inicializado.")


def cmd_import() -> None:
    from app.library_cache import rebuild_cache
    from app.library_migration import migrate_library_layout

    print("WARNING: 'import' esta deprecado; usa 'migrate-library-layout --apply' + 'rebuild-cache'.")
    stats = migrate_library_layout(apply_changes=True, create_backup=True)
    cache_stats = rebuild_cache()
    print("Migracion de biblioteca completada.")
    labels = {
        "mode": "Modo",
        "stories_detected": "Cuentos legacy detectados",
        "stories_migrated": "Cuentos migrados",
        "meta_created": "Meta creados",
        "pages_created": "Paginas creadas",
        "pages_skipped": "Paginas omitidas",
        "backups_created": "Backups creados",
        "pdf_copied": "PDF copiados",
    }
    _print_stats(stats, labels)
    print("Rebuild de cache completado.")
    cache_labels = {
        "nodes": "Nodos",
        "stories": "Cuentos",
        "pages": "Paginas",
        "slots": "Slots de imagen",
        "assets": "Assets indexados",
        "scanned_files": "Archivos escaneados",
        "cache_db": "DB de cache",
    }
    _print_stats(cache_stats, cache_labels)


def cmd_rebuild_cache() -> None:
    from app.library_cache import rebuild_cache

    stats = rebuild_cache()
    print("Cache reconstruida.")
    labels = {
        "nodes": "Nodos",
        "stories": "Cuentos",
        "pages": "Paginas",
        "slots": "Slots de imagen",
        "assets": "Assets indexados",
        "scanned_files": "Archivos escaneados",
        "cache_db": "DB de cache",
    }
    _print_stats(stats, labels)


def cmd_migrate_library_layout(apply: bool, create_backup: bool) -> None:
    from app.library_cache import rebuild_cache
    from app.library_migration import migrate_library_layout

    stats = migrate_library_layout(apply_changes=apply, create_backup=create_backup)
    mode_text = "aplicada" if apply else "simulada (dry-run)"
    print(f"Migracion de layout {mode_text}.")
    labels = {
        "mode": "Modo",
        "stories_detected": "Cuentos legacy detectados",
        "stories_migrated": "Cuentos migrados",
        "meta_created": "Meta creados",
        "pages_created": "Paginas creadas",
        "pages_skipped": "Paginas omitidas",
        "backups_created": "Backups creados",
        "pdf_copied": "PDF copiados",
    }
    _print_stats(stats, labels)
    if apply:
        cache_stats = rebuild_cache()
        print("Cache reconstruida tras migracion.")
        cache_labels = {
            "nodes": "Nodos",
            "stories": "Cuentos",
            "pages": "Paginas",
            "slots": "Slots de imagen",
            "assets": "Assets indexados",
            "scanned_files": "Archivos escaneados",
            "cache_db": "DB de cache",
        }
        _print_stats(cache_stats, cache_labels)


def cmd_migrate_texto_pages() -> None:
    from app.importer import migrate_texto_pages

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
    from app.importer import migrate_models_v3

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
    from app.importer import export_imagenes_backup

    stats = export_imagenes_backup(path)
    print("Exportacion de imagenes completada.")
    labels = {
        "imagenes_exportadas": "Imagenes exportadas",
        "ruta": "Archivo generado",
    }
    _print_stats(stats, labels)


def cmd_import_imagenes(path: str | None) -> None:
    from app.importer import import_imagenes_backup

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
    from app.importer import export_prompts_backup

    print("WARNING: export-prompts esta deprecado; usa export-imagenes.")
    stats = export_prompts_backup(path)
    labels = {
        "imagenes_exportadas": "Imagenes exportadas",
        "ruta": "Archivo generado",
    }
    _print_stats(stats, labels)


def cmd_import_prompts(path: str | None) -> None:
    from app.importer import import_prompts_backup

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
    from app import create_app

    app = create_app()
    app.run(host=host, port=port, debug=debug)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gestor web de Cuentos Cosmere")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Crear esquema de base de datos")
    sub.add_parser("import", help="Alias deprecado de migrate-library-layout --apply")
    sub.add_parser("migrate-texto-pages", help="Migrar tabla texto para usar numero_pagina")
    sub.add_parser("migrate-models-v3", help="Migrar modelos a Pagina/Ancla/Imagen")
    sub.add_parser("rebuild-cache", help="Reconstruir cache SQLite temporal desde biblioteca")

    migrate_layout = sub.add_parser(
        "migrate-library-layout",
        help="Migrar layout legacy (origen_md.md) a meta.md + NNN.md",
    )
    mode = migrate_layout.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Aplicar cambios en disco")
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo simular sin escribir archivos (por defecto)",
    )
    migrate_layout.add_argument(
        "--no-backup",
        action="store_true",
        help="No crear backup origen_md.legacy.md",
    )

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
    elif args.command == "rebuild-cache":
        cmd_rebuild_cache()
    elif args.command == "migrate-library-layout":
        cmd_migrate_library_layout(apply=bool(args.apply), create_backup=not bool(args.no_backup))
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
