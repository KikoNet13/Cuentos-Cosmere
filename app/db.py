from __future__ import annotations

from peewee import SqliteDatabase

from .config import DB_PATH

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

db = SqliteDatabase(
    DB_PATH,
    pragmas={
        "foreign_keys": 1,
        "journal_mode": "wal",
        "cache_size": -1024 * 64,
    },
)


def init_schema() -> None:
    from .models import (
        Cuento,
        HistorialEdicion,
        ImagenPrompt,
        Libro,
        Prompt,
        ReferenciaPDF,
        Saga,
        Texto,
    )

    db.connect(reuse_if_open=True)
    db.create_tables(
        [
            Saga,
            Libro,
            Cuento,
            Texto,
            Prompt,
            ImagenPrompt,
            ReferenciaPDF,
            HistorialEdicion,
        ],
        safe=True,
    )

