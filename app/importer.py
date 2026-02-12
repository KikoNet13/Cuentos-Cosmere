from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config import BASE_DIR, BIBLIOTECA_DIR, IMAGENES_BACKUP_JSON
from .db import db, init_schema
from .models import (
    Ancla,
    AnclaVersion,
    Cuento,
    Imagen,
    ImagenRequisito,
    Libro,
    Pagina,
    ReferenciaPDF,
    Saga,
)
from .text_pages import parse_markdown_pages
from .utils import read_text_with_fallback, slugify

SAGA_SLUG = "nacidos-de-la-bruma-era-1"
SAGA_NAME = "Nacidos de la bruma - Era 1"
LIBRO_SLUG = "el-imperio-final"
LIBRO_TITULO = "El Imperio Final"
CODIGO_RE = re.compile(r"^\d{2}$")
PAGE_NUMBER_RE = re.compile(r"(\d+)")


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


def _canonical_image_rel(cuento: Cuento, name: str) -> str:
    image_path = (
        BIBLIOTECA_DIR
        / cuento.libro.saga.slug
        / cuento.libro.slug
        / cuento.slug
        / "imagenes"
        / f"{name}.png"
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
        return IMAGENES_BACKUP_JSON
    candidate = Path(path_override).expanduser()
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate
    return candidate


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_rel_path(value: str) -> str:
    return value.strip().replace("\\", "/")


def _table_exists(name: str) -> bool:
    row = db.execute_sql(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return bool(row)


def _column_exists(table: str, column: str) -> bool:
    if not _table_exists(table):
        return False
    rows = db.execute_sql(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == column for r in rows)


def _ensure_schema_is_v3() -> None:
    if not _table_exists("pagina"):
        raise RuntimeError(
            "El esquema no esta en v3. Ejecuta: python manage.py migrate-models-v3"
        )


def _replace_story_pages(cuento: Cuento, src_md: Path, warnings: list[str]) -> tuple[int, int]:
    existing_pages = {
        row.numero: row
        for row in Pagina.select().where(Pagina.cuento == cuento).order_by(Pagina.numero.asc())
    }
    if not src_md.exists():
        deleted = Pagina.delete().where(Pagina.cuento == cuento).execute()
        warnings.append(f"[{cuento.codigo}] Falta {src_md.name}; paginas eliminadas ({deleted}).")
        return 0, int(deleted)

    markdown = read_text_with_fallback(src_md)
    pages, parse_warnings = parse_markdown_pages(markdown)
    warnings.extend(f"[{cuento.codigo}] {msg}" for msg in parse_warnings)

    incoming_numbers = set(pages.keys())
    now = _now_dt()
    imported = 0
    for numero in sorted(incoming_numbers):
        contenido = pages[numero]
        existing = existing_pages.get(numero)
        if existing:
            if existing.contenido != contenido:
                existing.contenido = contenido
            existing.updated_at = now
            existing.save()
        else:
            Pagina.create(
                cuento=cuento,
                numero=numero,
                contenido=contenido,
                created_at=now,
                updated_at=now,
            )
        imported += 1

    if incoming_numbers:
        deleted = (
            Pagina.delete()
            .where((Pagina.cuento == cuento) & (~(Pagina.numero.in_(sorted(incoming_numbers)))))
            .execute()
        )
    else:
        deleted = Pagina.delete().where(Pagina.cuento == cuento).execute()
    return imported, int(deleted)


def _import_canonical_files(libro: Libro) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "cuentos_detectados": 0,
        "paginas_importadas": 0,
        "paginas_eliminadas": 0,
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

        imported, deleted = _replace_story_pages(cuento, src_md, warnings)
        stats["paginas_importadas"] += imported
        stats["paginas_eliminadas"] += deleted
        if src_pdf.exists():
            _upsert_pdf(cuento, _relative_to_base(src_pdf))
            stats["pdf_refs"] += 1

    return stats


def _locate_cuento(saga_slug: str, libro_slug: str, cuento_codigo: str) -> Cuento | None:
    return Cuento.get_or_none(
        (Cuento.codigo == cuento_codigo)
        & (Cuento.libro.slug == libro_slug)
        & (Cuento.libro.saga.slug == saga_slug)
    )


def _locate_pagina(owner: dict[str, Any]) -> Pagina | None:
    saga_slug = str(owner.get("saga_slug", "")).strip()
    libro_slug = str(owner.get("libro_slug", "")).strip()
    cuento_codigo = str(owner.get("cuento_codigo", "")).strip()
    numero = _to_int(owner.get("pagina_numero"), 0)
    if not (saga_slug and libro_slug and cuento_codigo and numero > 0):
        return None
    cuento = _locate_cuento(saga_slug, libro_slug, cuento_codigo)
    if not cuento:
        return None
    return Pagina.get_or_none((Pagina.cuento == cuento) & (Pagina.numero == numero))


def _locate_or_create_ancla_version(owner: dict[str, Any]) -> AnclaVersion | None:
    saga_slug = str(owner.get("saga_slug", "")).strip()
    ancla_slug = str(owner.get("ancla_slug", "")).strip()
    version_name = str(owner.get("version_nombre", "")).strip()
    if not (saga_slug and ancla_slug and version_name):
        return None
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        return None
    ancla, _ = Ancla.get_or_create(
        saga=saga,
        slug=ancla_slug,
        defaults={
            "nombre": str(owner.get("ancla_nombre", ancla_slug)).strip() or ancla_slug,
            "tipo": str(owner.get("ancla_tipo", "otro")).strip() or "otro",
            "descripcion_base": str(owner.get("ancla_descripcion_base", "")),
            "estado": "activo",
            "created_at": _now_dt(),
            "updated_at": _now_dt(),
        },
    )
    version, _ = AnclaVersion.get_or_create(
        ancla=ancla,
        nombre_version=version_name,
        defaults={
            "descripcion": str(owner.get("version_descripcion", "")),
            "orden": _to_int(owner.get("version_orden"), 0),
            "estado": "activo",
            "created_at": _now_dt(),
            "updated_at": _now_dt(),
        },
    )
    return version


def _image_owner_payload(image: Imagen) -> dict[str, Any]:
    if image.owner_tipo == "pagina" and image.pagina_id and image.pagina:
        cuento = image.pagina.cuento
        return {
            "owner_tipo": "pagina",
            "saga_slug": cuento.libro.saga.slug,
            "libro_slug": cuento.libro.slug,
            "cuento_codigo": cuento.codigo,
            "pagina_numero": image.pagina.numero,
        }
    if image.owner_tipo == "ancla_version" and image.ancla_version_id and image.ancla_version:
        version = image.ancla_version
        ancla = version.ancla
        return {
            "owner_tipo": "ancla_version",
            "saga_slug": ancla.saga.slug,
            "ancla_slug": ancla.slug,
            "version_nombre": version.nombre_version,
        }
    return {"owner_tipo": image.owner_tipo}


def _image_locator(image: Imagen) -> dict[str, Any]:
    payload = _image_owner_payload(image)
    payload["rol"] = image.rol
    payload["orden"] = image.orden
    payload["ruta_relativa"] = image.ruta_relativa
    return payload


def export_imagenes_backup(path_override: str | None = None) -> dict[str, Any]:
    _ensure_schema_is_v3()
    target = _resolve_backup_path(path_override)
    target.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    for image in Imagen.select().order_by(Imagen.orden.asc(), Imagen.id.asc()):
        reqs: list[dict[str, Any]] = []
        for req in image.requisitos.order_by(ImagenRequisito.orden.asc(), ImagenRequisito.id.asc()):
            item: dict[str, Any] = {
                "origen_tipo": req.origen_tipo,
                "orden": req.orden,
                "nota": req.nota,
            }
            if req.origen_tipo == "ancla_version" and req.ancla_version:
                item["saga_slug"] = req.ancla_version.ancla.saga.slug
                item["ancla_slug"] = req.ancla_version.ancla.slug
                item["version_nombre"] = req.ancla_version.nombre_version
            elif req.origen_tipo == "imagen" and req.imagen_referencia:
                item["imagen_referencia"] = _image_locator(req.imagen_referencia)
            reqs.append(item)
        entries.append(
            {
                "owner": _image_owner_payload(image),
                "rol": image.rol,
                "principal_activa": bool(image.principal_activa),
                "ruta_relativa": image.ruta_relativa,
                "prompt_texto": image.prompt_texto,
                "requisitos_libres": image.get_requisitos_libres(),
                "orden": image.orden,
                "estado": image.estado,
                "updated_at": _dt_to_iso(image.updated_at),
                "requisitos": reqs,
            }
        )
    payload = {
        "meta": {
            "proyecto": "Cosmere - Imagenes v3",
            "version": "3.0.0",
            "updated_at": _now_dt().isoformat(),
            "total_imagenes": len(entries),
        },
        "entries": entries,
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"imagenes_exportadas": len(entries), "ruta": _display_path(target)}


def _find_image_by_locator(locator: dict[str, Any]) -> Imagen | None:
    owner_tipo = str(locator.get("owner_tipo", "")).strip()
    rol = str(locator.get("rol", "")).strip() or "principal"
    orden = _to_int(locator.get("orden"), 0)
    ruta_relativa = _normalize_rel_path(str(locator.get("ruta_relativa", "")))
    if owner_tipo == "pagina":
        pagina = _locate_pagina(locator)
        if not pagina:
            return None
        return Imagen.get_or_none(
            (Imagen.owner_tipo == "pagina")
            & (Imagen.pagina == pagina)
            & (Imagen.rol == rol)
            & (Imagen.orden == orden)
            & (Imagen.ruta_relativa == ruta_relativa)
        )
    if owner_tipo == "ancla_version":
        ancla_version = _locate_or_create_ancla_version(locator)
        if not ancla_version:
            return None
        return Imagen.get_or_none(
            (Imagen.owner_tipo == "ancla_version")
            & (Imagen.ancla_version == ancla_version)
            & (Imagen.rol == rol)
            & (Imagen.orden == orden)
            & (Imagen.ruta_relativa == ruta_relativa)
        )
    return None


def import_imagenes_backup(path_override: str | None = None) -> dict[str, Any]:
    _ensure_schema_is_v3()
    source = _resolve_backup_path(path_override)
    if not source.exists():
        raise FileNotFoundError(f"No existe archivo de backup: {_display_path(source)}")
    payload = json.loads(source.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = payload.get("entries", [])
    stats = {"imagenes_importadas": 0, "requisitos_importados": 0, "warnings": [], "ruta": _display_path(source)}
    for entry in entries:
        owner = entry.get("owner", {})
        owner_tipo = str(owner.get("owner_tipo", "")).strip()
        if owner_tipo == "pagina":
            pagina = _locate_pagina(owner)
            ancla_version = None
        elif owner_tipo == "ancla_version":
            pagina = None
            ancla_version = _locate_or_create_ancla_version(owner)
        else:
            stats["warnings"].append(f"Owner invalido: {owner}")
            continue
        if not pagina and not ancla_version:
            stats["warnings"].append(f"Owner no resuelto: {owner}")
            continue
        principal_flag = bool(entry.get("principal_activa", False)) and str(entry.get("rol", "principal")).strip() == "principal"
        if principal_flag and owner_tipo == "pagina" and pagina:
            (
                Imagen.update(principal_activa=False)
                .where((Imagen.owner_tipo == "pagina") & (Imagen.pagina == pagina) & (Imagen.rol == "principal"))
                .execute()
            )
        image = Imagen.create(
            pagina=pagina,
            ancla_version=ancla_version,
            owner_tipo=owner_tipo,
            rol=str(entry.get("rol", "principal")),
            principal_activa=principal_flag,
            ruta_relativa=_normalize_rel_path(str(entry.get("ruta_relativa", ""))),
            prompt_texto=str(entry.get("prompt_texto", "")),
            requisitos_libres_json=json.dumps([str(x) for x in entry.get("requisitos_libres", [])], ensure_ascii=False),
            orden=_to_int(entry.get("orden"), 0),
            estado=str(entry.get("estado", "activo")),
            created_at=_now_dt(),
            updated_at=_now_dt(),
        )
        stats["imagenes_importadas"] += 1
        for req in entry.get("requisitos", []):
            origen_tipo = str(req.get("origen_tipo", "")).strip()
            if origen_tipo == "ancla_version":
                ref = _locate_or_create_ancla_version(
                    {
                        "saga_slug": req.get("saga_slug"),
                        "ancla_slug": req.get("ancla_slug"),
                        "version_nombre": req.get("version_nombre"),
                    }
                )
                if ref:
                    ImagenRequisito.create(imagen=image, origen_tipo="ancla_version", ancla_version=ref, orden=_to_int(req.get("orden"), 0), nota=str(req.get("nota", "")))
                    stats["requisitos_importados"] += 1
            elif origen_tipo == "imagen":
                ref_image = _find_image_by_locator(req.get("imagen_referencia", {}))
                if ref_image:
                    ImagenRequisito.create(imagen=image, origen_tipo="imagen", imagen_referencia=ref_image, orden=_to_int(req.get("orden"), 0), nota=str(req.get("nota", "")))
                    stats["requisitos_importados"] += 1
    return stats


def export_prompts_backup(path_override: str | None = None) -> dict[str, Any]:
    stats = export_imagenes_backup(path_override)
    stats["warnings"] = ["Comando deprecado: usa 'export-imagenes'."]
    return stats


def import_prompts_backup(path_override: str | None = None) -> dict[str, Any]:
    stats = import_imagenes_backup(path_override)
    warnings = list(stats.get("warnings", []))
    warnings.insert(0, "Comando deprecado: usa 'import-imagenes'.")
    stats["warnings"] = warnings
    return stats


def _create_v3_tables() -> None:
    db.execute_sql(
        """
        CREATE TABLE IF NOT EXISTS pagina (
            id VARCHAR(255) NOT NULL PRIMARY KEY,
            cuento_id VARCHAR(255) NOT NULL,
            numero INTEGER NOT NULL,
            contenido TEXT NOT NULL DEFAULT '',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (cuento_id) REFERENCES cuento (id) ON DELETE CASCADE
        )
        """
    )
    db.execute_sql(
        'CREATE UNIQUE INDEX IF NOT EXISTS "pagina_cuento_numero_uq" '
        'ON "pagina" ("cuento_id", "numero")'
    )
    db.execute_sql(
        """
        CREATE TABLE IF NOT EXISTS ancla (
            id VARCHAR(255) NOT NULL PRIMARY KEY,
            saga_id VARCHAR(255) NOT NULL,
            slug VARCHAR(255) NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            tipo VARCHAR(255) NOT NULL DEFAULT 'otro',
            descripcion_base TEXT NOT NULL DEFAULT '',
            estado VARCHAR(255) NOT NULL DEFAULT 'activo',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (saga_id) REFERENCES saga (id) ON DELETE CASCADE
        )
        """
    )
    db.execute_sql(
        'CREATE UNIQUE INDEX IF NOT EXISTS "ancla_saga_slug_uq" '
        'ON "ancla" ("saga_id", "slug")'
    )
    db.execute_sql(
        """
        CREATE TABLE IF NOT EXISTS ancla_version (
            id VARCHAR(255) NOT NULL PRIMARY KEY,
            ancla_id VARCHAR(255) NOT NULL,
            nombre_version VARCHAR(255) NOT NULL,
            descripcion TEXT NOT NULL DEFAULT '',
            orden INTEGER NOT NULL DEFAULT 0,
            estado VARCHAR(255) NOT NULL DEFAULT 'activo',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (ancla_id) REFERENCES ancla (id) ON DELETE CASCADE
        )
        """
    )
    db.execute_sql(
        'CREATE UNIQUE INDEX IF NOT EXISTS "ancla_version_ancla_nombre_uq" '
        'ON "ancla_version" ("ancla_id", "nombre_version")'
    )
    db.execute_sql(
        """
        CREATE TABLE IF NOT EXISTS imagen (
            id VARCHAR(255) NOT NULL PRIMARY KEY,
            pagina_id VARCHAR(255),
            ancla_version_id VARCHAR(255),
            owner_tipo VARCHAR(32) NOT NULL,
            rol VARCHAR(32) NOT NULL,
            principal_activa INTEGER NOT NULL DEFAULT 0,
            ruta_relativa TEXT NOT NULL DEFAULT '',
            prompt_texto TEXT NOT NULL DEFAULT '',
            requisitos_libres_json TEXT NOT NULL DEFAULT '[]',
            orden INTEGER NOT NULL DEFAULT 0,
            estado VARCHAR(255) NOT NULL DEFAULT 'activo',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (pagina_id) REFERENCES pagina (id) ON DELETE CASCADE,
            FOREIGN KEY (ancla_version_id) REFERENCES ancla_version (id) ON DELETE CASCADE
        )
        """
    )
    db.execute_sql(
        'CREATE UNIQUE INDEX IF NOT EXISTS "imagen_pagina_principal_activa_uq" '
        'ON "imagen" ("pagina_id") '
        "WHERE pagina_id IS NOT NULL AND rol='principal' AND principal_activa=1"
    )
    db.execute_sql(
        """
        CREATE TABLE IF NOT EXISTS imagen_requisito (
            id VARCHAR(255) NOT NULL PRIMARY KEY,
            imagen_id VARCHAR(255) NOT NULL,
            origen_tipo VARCHAR(32) NOT NULL,
            ancla_version_id VARCHAR(255),
            imagen_referencia_id VARCHAR(255),
            orden INTEGER NOT NULL DEFAULT 0,
            nota TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (imagen_id) REFERENCES imagen (id) ON DELETE CASCADE,
            FOREIGN KEY (ancla_version_id) REFERENCES ancla_version (id) ON DELETE CASCADE,
            FOREIGN KEY (imagen_referencia_id) REFERENCES imagen (id) ON DELETE CASCADE
        )
        """
    )


def _migrate_texto_legacy(warnings: list[str]) -> int:
    if not _table_exists("texto"):
        return 0
    moved = 0
    now = _now_dt()
    if _column_exists("texto", "numero_pagina"):
        rows = db.execute_sql(
            "SELECT id, cuento_id, numero_pagina, contenido, created_at, updated_at FROM texto"
        ).fetchall()
        for rid, cuento_id, numero, contenido, created_at, updated_at in rows:
            db.execute_sql(
                """
                INSERT INTO pagina (id, cuento_id, numero, contenido, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(cuento_id, numero) DO UPDATE SET
                    contenido=excluded.contenido,
                    updated_at=excluded.updated_at
                """,
                (rid or str(uuid4()), cuento_id, int(numero), contenido or "", created_at or now, updated_at or now),
            )
            moved += 1
    else:
        rows = db.execute_sql(
            "SELECT cuento_id, tipo, contenido, created_at, updated_at FROM texto ORDER BY cuento_id, updated_at"
        ).fetchall()
        latest_md: dict[str, tuple[str, Any, Any]] = {}
        for cuento_id, tipo, contenido, created_at, updated_at in rows:
            if tipo == "md":
                latest_md[cuento_id] = (contenido or "", created_at, updated_at)
        for cuento_id, (markdown, created_at, updated_at) in latest_md.items():
            pages, parse_warnings = parse_markdown_pages(markdown)
            warnings.extend(f"[{cuento_id}] {msg}" for msg in parse_warnings)
            for numero, contenido in pages.items():
                db.execute_sql(
                    """
                    INSERT INTO pagina (id, cuento_id, numero, contenido, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(cuento_id, numero) DO UPDATE SET
                        contenido=excluded.contenido,
                        updated_at=excluded.updated_at
                    """,
                    (str(uuid4()), cuento_id, int(numero), contenido, created_at or now, updated_at or now),
                )
                moved += 1
    db.execute_sql('DROP TABLE IF EXISTS "texto"')
    return moved


def _prompt_to_page_num(raw: str) -> int | None:
    match = PAGE_NUMBER_RE.search(raw or "")
    if not match:
        return None
    try:
        value = int(match.group(1))
    except ValueError:
        return None
    return value if value > 0 else None


def _migrate_prompt_legacy(warnings: list[str]) -> dict[str, int]:
    if not _table_exists("prompt"):
        return {"prompts_migrados": 0, "imagenes_migradas": 0}
    page_map = {
        (cuento_id, int(numero)): page_id
        for page_id, cuento_id, numero in db.execute_sql(
            "SELECT id, cuento_id, numero FROM pagina"
        ).fetchall()
    }
    rows = db.execute_sql(
        """
        SELECT p.id_prompt, p.cuento_id, p.pagina, p.tipo_imagen, p.descripcion,
               p.detalles_importantes_json, p.prompt_final_literal, p.bloque_copy_paste,
               p.orden, p.estado, p.updated_at, ip.ruta_relativa
        FROM prompt p
        LEFT JOIN imagenprompt ip ON ip.prompt_id = p.id
        ORDER BY p.cuento_id, p.orden, p.id_prompt
        """
    ).fetchall()
    moved = 0
    now = _now_dt()
    for id_prompt, cuento_id, pagina_raw, tipo_imagen, descripcion, detalles, final_text, bloque_text, orden, estado, updated_at, ruta in rows:
        page_num = _prompt_to_page_num(str(pagina_raw or ""))
        if page_num is None:
            warnings.append(f"Prompt {id_prompt}: pagina invalida '{pagina_raw}'.")
            continue
        pagina_id = page_map.get((cuento_id, page_num))
        if not pagina_id:
            warnings.append(f"Prompt {id_prompt}: no existe pagina {page_num}.")
            continue
        role = "principal" if str(tipo_imagen or "").strip().lower() == "principal" else ("referencia" if str(tipo_imagen or "").strip().lower() == "referencia" else "secundaria")
        prompt_text = str(final_text or "").strip() or str(bloque_text or "").strip() or str(descripcion or "").strip()
        try:
            detalles_list = json.loads(detalles or "[]")
        except json.JSONDecodeError:
            detalles_list = []
        rel = _normalize_rel_path(str(ruta or ""))
        if not rel:
            rel = f"biblioteca/imagenes/{id_prompt}.png"
        db.execute_sql(
            """
            INSERT INTO imagen (
                id, pagina_id, ancla_version_id, owner_tipo, rol, principal_activa,
                ruta_relativa, prompt_texto, requisitos_libres_json, orden, estado, created_at, updated_at
            ) VALUES (?, ?, NULL, 'pagina', ?, 0, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(uuid4()), pagina_id, role, rel, prompt_text, json.dumps(detalles_list, ensure_ascii=False), _to_int(orden, 0), str(estado or "activo"), now, updated_at or now),
        )
        moved += 1
    for pagina_id, in db.execute_sql("SELECT id FROM pagina").fetchall():
        principals = [r[0] for r in db.execute_sql("SELECT id FROM imagen WHERE pagina_id=? AND rol='principal' ORDER BY orden,id", (pagina_id,)).fetchall()]
        db.execute_sql("UPDATE imagen SET principal_activa=0 WHERE pagina_id=?", (pagina_id,))
        if principals:
            db.execute_sql("UPDATE imagen SET principal_activa=1 WHERE id=?", (principals[0],))
    db.execute_sql('DROP TABLE IF EXISTS "imagenprompt"')
    db.execute_sql('DROP TABLE IF EXISTS "prompt"')
    return {"prompts_migrados": moved, "imagenes_migradas": moved}


def migrate_models_v3() -> dict[str, Any]:
    init_schema()
    db.connect(reuse_if_open=True)
    warnings: list[str] = []
    had_texto = _table_exists("texto")
    had_prompt = _table_exists("prompt")
    with db.atomic():
        db.execute_sql("PRAGMA foreign_keys=OFF;")
        try:
            _create_v3_tables()
            pages_migradas = _migrate_texto_legacy(warnings)
            prompt_stats = _migrate_prompt_legacy(warnings)
        finally:
            db.execute_sql("PRAGMA foreign_keys=ON;")
    return {
        "estado": "sin_cambios" if not had_texto and not had_prompt else "ok",
        "paginas_migradas": pages_migradas,
        "prompts_migrados": int(prompt_stats.get("prompts_migrados", 0)),
        "imagenes_migradas": int(prompt_stats.get("imagenes_migradas", 0)),
        "warnings": warnings,
    }


def migrate_texto_pages() -> dict[str, Any]:
    stats = migrate_models_v3()
    warnings = list(stats.get("warnings", []))
    warnings.insert(0, "Comando deprecado: usa 'migrate-models-v3'.")
    stats["warnings"] = warnings
    return stats


def import_initial_dataset() -> dict[str, Any]:
    init_schema()
    db.connect(reuse_if_open=True)
    _ensure_schema_is_v3()
    saga, libro = _get_or_create_domain()
    base_stats = _import_canonical_files(libro)
    return {
        "sagas": Saga.select().count(),
        "libros": Libro.select().count(),
        "cuentos": Cuento.select().count(),
        "paginas": Pagina.select().count(),
        "anclas": Ancla.select().count(),
        "versiones_ancla": AnclaVersion.select().count(),
        "imagenes": Imagen.select().count(),
        "requisitos_imagen": ImagenRequisito.select().count(),
        "referencias_pdf": ReferenciaPDF.select().count(),
        "cuentos_detectados": int(base_stats["cuentos_detectados"]),
        "paginas_importadas": int(base_stats["paginas_importadas"]),
        "paginas_eliminadas": int(base_stats["paginas_eliminadas"]),
        "pdf_refs": int(base_stats["pdf_refs"]),
        "warnings": list(base_stats["warnings"]),
        "saga_slug": saga.slug,
        "libro_slug": libro.slug,
    }
