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
        Ancla,
        AnclaVersion,
        Cuento,
        HistorialEdicion,
        Imagen,
        ImagenRequisito,
        Libro,
        Pagina,
        ReferenciaPDF,
        Saga,
    )

    db.connect(reuse_if_open=True)
    db.create_tables(
        [
            Saga,
            Libro,
            Cuento,
            Pagina,
            Ancla,
            AnclaVersion,
            Imagen,
            ImagenRequisito,
            ReferenciaPDF,
            HistorialEdicion,
        ],
        safe=True,
    )
    db.execute_sql(
        'CREATE UNIQUE INDEX IF NOT EXISTS "imagen_pagina_principal_activa_uq" '
        'ON "imagen" ("pagina_id") '
        "WHERE pagina_id IS NOT NULL AND rol='principal' AND principal_activa=1"
    )
