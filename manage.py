from __future__ import annotations

import argparse
import sys

from app.config import APP_TITLE


def _print_stats(stats: dict[str, object], labels: dict[str, str]) -> None:
    warnings = stats.get("warnings", [])
    for key, value in stats.items():
        if key == "warnings":
            continue
        print(f"{labels.get(key, key)}: {value}")
    if isinstance(warnings, list):
        for warning in warnings:
            print(f"WARNING: {warning}")


def cmd_rebuild_cache() -> None:
    from app.library_cache import rebuild_cache

    stats = rebuild_cache()
    print("Caché reconstruida.")
    labels = {
        "nodes": "Nodos",
        "stories": "Cuentos",
        "pages": "Páginas",
        "slots": "Slots de imagen",
        "assets": "Assets indexados",
        "scanned_files": "Archivos escaneados",
        "cache_db": "DB de caché",
        "fingerprint": "Fingerprint",
    }
    _print_stats(stats, labels)


def cmd_migrate_library_layout(apply: bool, create_backup: bool) -> None:
    from app.library_cache import rebuild_cache
    from app.library_migration import migrate_library_layout

    stats = migrate_library_layout(apply_changes=apply, create_backup=create_backup)
    mode_text = "aplicada" if apply else "simulada (dry-run)"
    print(f"Migración de layout {mode_text}.")

    labels = {
        "mode": "Modo",
        "stories_detected": "Cuentos legacy detectados",
        "stories_migrated": "Cuentos migrados",
        "meta_created": "Meta creados",
        "pages_created": "Páginas creadas",
        "pages_updated": "Páginas actualizadas",
        "pages_skipped": "Páginas omitidas",
        "md_backups_created": "Backups MD creados",
        "pdf_copied": "PDF copiados",
        "anchors_guide_updated": "Guías de anclas actualizadas",
        "anchor_entries": "Entradas de anclas",
        "legacy_prompt_retired": "JSON legacy retirados",
    }
    _print_stats(stats, labels)

    if apply:
        cache_stats = rebuild_cache()
        print("Caché reconstruida tras la migración.")
        cache_labels = {
            "nodes": "Nodos",
            "stories": "Cuentos",
            "pages": "Páginas",
            "slots": "Slots de imagen",
            "assets": "Assets indexados",
            "scanned_files": "Archivos escaneados",
            "cache_db": "DB de caché",
            "fingerprint": "Fingerprint",
        }
        _print_stats(cache_stats, cache_labels)


def cmd_runserver(host: str, port: int, debug: bool) -> None:
    from app import create_app

    app = create_app()
    app.run(host=host, port=port, debug=debug)


def main() -> None:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "rebuild-cache",
        help="Reconstruir caché temporal desde biblioteca",
    )

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
        help="No crear archivos *.legacy.*",
    )

    run = sub.add_parser("runserver", help="Ejecutar servidor de desarrollo Flask")
    run.add_argument("--host", default="127.0.0.1", help="Host de escucha")
    run.add_argument("--port", type=int, default=5000, help="Puerto de escucha")
    run.add_argument("--debug", action="store_true", help="Activar modo depuración")

    args = parser.parse_args()

    if args.command == "rebuild-cache":
        cmd_rebuild_cache()
    elif args.command == "migrate-library-layout":
        cmd_migrate_library_layout(apply=bool(args.apply), create_backup=not bool(args.no_backup))
    elif args.command == "runserver":
        cmd_runserver(host=args.host, port=args.port, debug=args.debug)
    else:
        print(f"ERROR: comando no soportado: {args.command}")
        sys.exit(2)


if __name__ == "__main__":
    main()