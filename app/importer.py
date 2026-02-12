from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import BASE_DIR, BIBLIOTECA_DIR, PROMPTS_BACKUP_JSON
from .db import db, init_schema
from .models import Cuento, ImagenPrompt, Libro, Prompt, ReferenciaPDF, Saga, Texto
from .text_pages import EXPECTED_PAGE_COUNT, parse_markdown_pages
from .utils import read_text_with_fallback, slugify

SAGA_SLUG = "nacidos-de-la-bruma-era-1"
SAGA_NAME = "Nacidos de la bruma - Era 1"
LIBRO_SLUG = "el-imperio-final"
LIBRO_TITULO = "El Imperio Final"
CODIGO_RE = re.compile(r"^\d{2}$")


def _now_dt():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0)


def _relative_to_base(path: Path) -> str:
    return path.resolve().relative_to(BASE_DIR.resolve()).as_posix()


def _display_path(path: Path) -> str:
    try:
        return _relative_to_base(path)
    except ValueError:
        return str(path)


def _canonical_book_dir() -> Path:
    return BIBLIOTECA_DIR / SAGA_SLUG / LIBRO_SLUG


def _get_or_create_domain() -> tuple[Saga, Libro]:
    saga, _ = Saga.get_or_create(
        slug=SAGA_SLUG,
        defaults={"nombre": SAGA_NAME, "descripcion": "Saga importada desde estructura local."},
    )
    libro, _ = Libro.get_or_create(
        saga=saga,
        slug=LIBRO_SLUG,
        defaults={"titulo": LIBRO_TITULO, "orden": 1},
    )
    return saga, libro


def _cuento_from_codigo(libro: Libro, codigo: str) -> Cuento:
    cuento_slug = slugify(codigo)
    orden = int(codigo) if CODIGO_RE.fullmatch(codigo) else 0
    cuento, _ = Cuento.get_or_create(
        libro=libro,
        slug=cuento_slug,
        defaults={
            "codigo": codigo,
            "titulo": codigo,
            "estado": "activo",
            "orden": orden,
        },
    )
    if cuento.codigo != codigo:
        cuento.codigo = codigo
        cuento.updated_at = _now_dt()
        cuento.save()
    return cuento


def _canonical_image_rel(cuento: Cuento, id_prompt: str) -> str:
    image_path = (
        BIBLIOTECA_DIR
        / cuento.libro.saga.slug
        / cuento.libro.slug
        / cuento.slug
        / "imagenes"
        / f"{id_prompt}.png"
    )
    return _relative_to_base(image_path)


def _dt_to_iso(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _upsert_pdf(cuento: Cuento, ruta_pdf: str) -> None:
    ref, created = ReferenciaPDF.get_or_create(
        cuento=cuento,
        ruta_pdf=ruta_pdf,
        defaults={"notas": "Referencia externa al PDF del libro."},
    )
    if not created:
        ref.updated_at = _now_dt()
        ref.save()


def _resolve_backup_path(path_override: str | None) -> Path:
    if not path_override:
        return PROMPTS_BACKUP_JSON
    candidate = Path(path_override).expanduser()
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate
    return candidate


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _ensure_texto_schema_is_paginated() -> None:
    columns = [row[1] for row in db.execute_sql("PRAGMA table_info(texto)").fetchall()]
    if "numero_pagina" not in columns:
        raise RuntimeError(
            "El esquema de 'texto' no tiene 'numero_pagina'. "
            "Ejecuta: python manage.py migrate-texto-pages"
        )


def _replace_story_pages(cuento: Cuento, src_md: Path, warnings: list[str]) -> int:
    Texto.delete().where(Texto.cuento == cuento).execute()
    if not src_md.exists():
        warnings.append(f"[{cuento.codigo}] Falta {src_md.name}; texto vaciado.")
        return 0

    markdown = read_text_with_fallback(src_md)
    pages, parse_warnings = parse_markdown_pages(markdown)
    warnings.extend(f"[{cuento.codigo}] {msg}" for msg in parse_warnings)
    if len(pages) != EXPECTED_PAGE_COUNT:
        warnings.append(
            f"[{cuento.codigo}] Se detectaron {len(pages)} paginas; esperado {EXPECTED_PAGE_COUNT}."
        )

    now = _now_dt()
    for numero_pagina in sorted(pages):
        Texto.create(
            cuento=cuento,
            numero_pagina=numero_pagina,
            contenido=pages[numero_pagina],
            created_at=now,
            updated_at=now,
        )
    return len(pages)


def _import_canonical_files(libro: Libro) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "cuentos_detectados": 0,
        "textos_importados": 0,
        "pdf_refs": 0,
        "warnings": [],
    }
    warnings: list[str] = stats["warnings"]

    book_dir = _canonical_book_dir()
    if not book_dir.exists():
        warnings.append(f"No existe el directorio canonico: {_display_path(book_dir)}")
        return stats

    codes = sorted(
        p.name for p in book_dir.iterdir() if p.is_dir() and CODIGO_RE.fullmatch(p.name)
    )
    for code in codes:
        cuento = _cuento_from_codigo(libro, code)
        stats["cuentos_detectados"] += 1

        textos_dir = book_dir / code / "textos"
        src_md = textos_dir / "origen_md.md"
        src_pdf = textos_dir / "referencia_pdf.pdf"

        stats["textos_importados"] += _replace_story_pages(cuento, src_md, warnings)
        if src_pdf.exists():
            _upsert_pdf(cuento, _relative_to_base(src_pdf))
            stats["pdf_refs"] += 1

    return stats


def _prompt_entry(prompt: Prompt) -> dict[str, Any]:
    image = ImagenPrompt.get_or_none(ImagenPrompt.prompt == prompt)
    image_rel = image.ruta_relativa if image else _canonical_image_rel(prompt.cuento, prompt.id_prompt)
    return {
        "id_prompt": prompt.id_prompt,
        "bloque": prompt.bloque,
        "pagina": prompt.pagina,
        "tipo_imagen": prompt.tipo_imagen,
        "grupo": prompt.grupo,
        "generar_una_imagen_de": prompt.generar_una_imagen_de,
        "descripcion": prompt.descripcion,
        "detalles_importantes": prompt.get_detalles(),
        "prompt_final_literal": prompt.prompt_final_literal,
        "bloque_copy_paste": prompt.bloque_copy_paste,
        "imagen_rel_path": image_rel,
        "orden": prompt.orden,
        "estado": prompt.estado,
        "updated_at": _dt_to_iso(prompt.updated_at),
    }


def export_prompts_backup(path_override: str | None = None) -> dict[str, Any]:
    target = _resolve_backup_path(path_override)
    target.parent.mkdir(parents=True, exist_ok=True)
    entries = [_prompt_entry(prompt) for prompt in Prompt.select().order_by(Prompt.orden, Prompt.id_prompt)]
    payload = {
        "meta": {
            "proyecto": "Cosmere - Mistborn Era 1 - Imagenes",
            "version": "2.0.0",
            "updated_at": _now_dt().isoformat(),
            "total_prompts": len(entries),
            "notas": "Fuente canonica: base SQLite. Archivo generado con export-prompts.",
        },
        "entries": entries,
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "prompts_exportados": len(entries),
        "ruta": _display_path(target),
    }


def import_prompts_backup(path_override: str | None = None) -> dict[str, Any]:
    source = _resolve_backup_path(path_override)
    if not source.exists():
        raise FileNotFoundError(f"No existe archivo de backup: {_display_path(source)}")

    payload = json.loads(source.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = payload.get("entries", [])
    _, libro = _get_or_create_domain()
    stats: dict[str, Any] = {
        "prompts_importados": 0,
        "imagenes_map": 0,
        "prompts_omitidos_bloque_invalido": 0,
        "warnings": [],
        "ruta": _display_path(source),
    }
    warnings: list[str] = stats["warnings"]

    for entry in entries:
        codigo = str(entry.get("bloque", "")).strip()
        if not CODIGO_RE.fullmatch(codigo):
            stats["prompts_omitidos_bloque_invalido"] += 1
            warnings.append(f"Bloque invalido en prompt: {entry.get('id_prompt', '(sin id)')}")
            continue

        id_prompt = str(entry.get("id_prompt", "")).strip()
        if not id_prompt:
            warnings.append("Prompt omitido por id_prompt vacio.")
            continue

        cuento = _cuento_from_codigo(libro, codigo)
        prompt, _ = Prompt.get_or_create(id_prompt=id_prompt, defaults={"cuento": cuento})
        prompt.cuento = cuento
        prompt.bloque = codigo
        prompt.pagina = str(entry.get("pagina", ""))
        prompt.tipo_imagen = str(entry.get("tipo_imagen", "principal"))
        prompt.grupo = str(entry.get("grupo", "piloto"))
        prompt.generar_una_imagen_de = str(entry.get("generar_una_imagen_de", ""))
        prompt.descripcion = str(entry.get("descripcion", ""))
        prompt.set_detalles([str(x) for x in entry.get("detalles_importantes", [])])
        prompt.prompt_final_literal = str(entry.get("prompt_final_literal", ""))
        prompt.bloque_copy_paste = str(entry.get("bloque_copy_paste", ""))
        prompt.orden = _to_int(entry.get("orden"), 0)
        prompt.estado = str(entry.get("estado", "activo"))
        prompt.updated_at = _now_dt()
        prompt.save()

        image_rel = str(entry.get("imagen_rel_path", "")).strip() or _canonical_image_rel(cuento, id_prompt)
        image_rel = image_rel.replace("\\", "/")
        image_exists = (BASE_DIR / image_rel).exists()
        image, created = ImagenPrompt.get_or_create(
            prompt=prompt,
            defaults={
                "ruta_relativa": image_rel,
                "existe_archivo": image_exists,
                "updated_at": _now_dt(),
            },
        )
        if not created:
            image.ruta_relativa = image_rel
            image.existe_archivo = image_exists
            image.updated_at = _now_dt()
            image.save()

        stats["prompts_importados"] += 1
        stats["imagenes_map"] += 1

    return stats


def migrate_texto_pages() -> dict[str, Any]:
    db.connect(reuse_if_open=True)
    columns = [row[1] for row in db.execute_sql("PRAGMA table_info(texto)").fetchall()]
    if "numero_pagina" in columns and "tipo" not in columns:
        return {"paginas_migradas": Texto.select().count(), "warnings": [], "estado": "sin_cambios"}

    rows = list(
        db.execute_sql(
            """
            SELECT cuento_id, tipo, contenido, created_at, updated_at
            FROM texto
            ORDER BY cuento_id ASC, updated_at ASC
            """
        ).fetchall()
    )

    warnings: list[str] = []
    md_by_cuento: dict[str, tuple[str, Any, Any]] = {}
    for cuento_id, tipo, contenido, created_at, updated_at in rows:
        if tipo != "md":
            continue
        if cuento_id in md_by_cuento:
            warnings.append(f"[{cuento_id}] Multiples fuentes md; se usa la mas reciente.")
        md_by_cuento[cuento_id] = (contenido or "", created_at, updated_at)

    inserts: list[tuple[str, str, int, str, Any, Any]] = []
    for cuento_id, (markdown, created_at, updated_at) in md_by_cuento.items():
        pages, parse_warnings = parse_markdown_pages(markdown)
        warnings.extend(f"[{cuento_id}] {msg}" for msg in parse_warnings)
        if len(pages) != EXPECTED_PAGE_COUNT:
            warnings.append(
                f"[{cuento_id}] Se detectaron {len(pages)} paginas; esperado {EXPECTED_PAGE_COUNT}."
            )
        for numero_pagina in sorted(pages):
            inserts.append(
                (
                    str(uuid4()),
                    cuento_id,
                    numero_pagina,
                    pages[numero_pagina],
                    created_at,
                    updated_at,
                )
            )

    with db.atomic():
        db.execute_sql("PRAGMA foreign_keys=OFF;")
        try:
            db.execute_sql(
                """
                CREATE TABLE texto_new (
                    id VARCHAR(255) NOT NULL PRIMARY KEY,
                    cuento_id VARCHAR(255) NOT NULL,
                    numero_pagina INTEGER NOT NULL,
                    contenido TEXT NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY (cuento_id) REFERENCES cuento (id) ON DELETE CASCADE
                )
                """
            )
            if inserts:
                db.connection().executemany(
                    """
                    INSERT INTO texto_new
                    (id, cuento_id, numero_pagina, contenido, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    inserts,
                )
            db.execute_sql('DROP TABLE "texto"')
            db.execute_sql('ALTER TABLE "texto_new" RENAME TO "texto"')
            db.execute_sql('CREATE INDEX "texto_cuento_id" ON "texto" ("cuento_id")')
            db.execute_sql(
                'CREATE UNIQUE INDEX "texto_cuento_id_numero_pagina" '
                'ON "texto" ("cuento_id", "numero_pagina")'
            )
        finally:
            db.execute_sql("PRAGMA foreign_keys=ON;")

    return {
        "paginas_migradas": len(inserts),
        "cuentos_migrados": len(md_by_cuento),
        "warnings": warnings,
        "estado": "ok",
    }


def import_initial_dataset() -> dict[str, Any]:
    init_schema()
    db.connect(reuse_if_open=True)
    _ensure_texto_schema_is_paginated()
    saga, libro = _get_or_create_domain()

    base_stats = _import_canonical_files(libro)

    return {
        "sagas": Saga.select().count(),
        "libros": Libro.select().count(),
        "cuentos": Cuento.select().count(),
        "textos": Texto.select().count(),
        "referencias_pdf": ReferenciaPDF.select().count(),
        "prompts": Prompt.select().count(),
        "imagenes_prompt": ImagenPrompt.select().count(),
        "cuentos_detectados": int(base_stats["cuentos_detectados"]),
        "textos_importados": int(base_stats["textos_importados"]),
        "pdf_refs": int(base_stats["pdf_refs"]),
        "warnings": list(base_stats["warnings"]),
        "saga_slug": saga.slug,
        "libro_slug": libro.slug,
    }
