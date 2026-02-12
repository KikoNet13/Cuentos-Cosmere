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
        "book_nodes_detected": "Nodos libro detectados",
        "stories_detected": "Cuentos detectados",
        "stories_migrated": "Cuentos migrados",
        "story_files_created": "Archivos NN.md creados",
        "story_files_updated": "Archivos NN.md actualizados",
        "pdf_copied": "PDF copiados",
        "images_copied": "Imágenes copiadas",
        "legacy_dirs_archived": "Directorios legacy archivados",
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


def cmd_inbox_parse(input_path: str, book_rel_path: str, story_id: str) -> None:
    from app.notebooklm_ingest import inbox_parse

    stats = inbox_parse(input_path=input_path, book_rel_path=book_rel_path, story_id=story_id)
    print("Propuesta de inbox generada.")
    labels = {
        "batch_id": "Batch",
        "book_rel_path": "Libro",
        "story_id": "Cuento",
        "title": "Título",
        "pages_detected": "Páginas detectadas",
        "manifest": "Manifest",
        "proposal": "Propuesta",
    }
    _print_stats(stats, labels)


def cmd_inbox_apply(batch_id: str, approve: bool, force: bool) -> None:
    from app.library_cache import rebuild_cache
    from app.notebooklm_ingest import inbox_apply

    stats = inbox_apply(batch_id=batch_id, approve=approve, force=force)
    print("Propuesta aplicada a canónico.")
    labels = {
        "batch_id": "Batch",
        "story_id": "Cuento",
        "book_rel_path": "Libro",
        "target": "Destino",
        "backup_created": "Backup previo",
    }
    _print_stats(stats, labels)

    cache_stats = rebuild_cache()
    print("Caché reconstruida tras aplicar propuesta.")
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
        help="Reconstruir caché temporal desde library",
    )

    migrate_layout = sub.add_parser(
        "migrate-library-layout",
        help="Migrar layout legacy a libro plano con cuentos NN.md",
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
        help="No archivar directorios legacy",
    )

    inbox_parse = sub.add_parser(
        "inbox-parse",
        help="Parsear un markdown de entrada y generar propuesta en library/_inbox",
    )
    inbox_parse.add_argument("--input", required=True, help="Ruta del markdown de entrada")
    inbox_parse.add_argument("--book", required=True, help="Ruta relativa del nodo libro dentro de library")
    inbox_parse.add_argument("--story-id", required=True, help="ID de cuento de 2 dígitos (NN)")

    inbox_apply = sub.add_parser(
        "inbox-apply",
        help="Aplicar una propuesta desde library/_inbox al canónico",
    )
    inbox_apply.add_argument("--batch-id", required=True, help="ID del batch a aplicar")
    inbox_apply.add_argument("--approve", action="store_true", help="Confirmar aplicación")
    inbox_apply.add_argument("--force", action="store_true", help="Forzar aplicación aunque status no sea proposed")

    run = sub.add_parser("runserver", help="Ejecutar servidor de desarrollo Flask")
    run.add_argument("--host", default="127.0.0.1", help="Host de escucha")
    run.add_argument("--port", type=int, default=5000, help="Puerto de escucha")
    run.add_argument("--debug", action="store_true", help="Activar modo depuración")

    args = parser.parse_args()

    if args.command == "rebuild-cache":
        cmd_rebuild_cache()
    elif args.command == "migrate-library-layout":
        cmd_migrate_library_layout(apply=bool(args.apply), create_backup=not bool(args.no_backup))
    elif args.command == "inbox-parse":
        cmd_inbox_parse(input_path=args.input, book_rel_path=args.book, story_id=args.story_id)
    elif args.command == "inbox-apply":
        cmd_inbox_apply(batch_id=args.batch_id, approve=bool(args.approve), force=bool(args.force))
    elif args.command == "runserver":
        cmd_runserver(host=args.host, port=args.port, debug=args.debug)
    else:
        print(f"ERROR: comando no soportado: {args.command}")
        sys.exit(2)


if __name__ == "__main__":
    main()
