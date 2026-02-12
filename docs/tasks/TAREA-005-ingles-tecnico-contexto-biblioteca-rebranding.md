# TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding

## Metadatos

- ID de tarea: `TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding`
- Fecha: 12/02/26 19:15
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0003`, `0004`

## Objetivo

Completar el refactor total solicitado: inglés técnico en código activo,
castellano visible, limpieza de contexto, renombre de PDF canónico,
eliminación de capa legacy relacional y rebranding a
**Generador de cuentos ilustrados**.

## Contexto

El repositorio todavía mantenía referencias legacy y branding antiguo en
código, documentación y contratos de archivos.

## Plan

1. Cerrar el refactor técnico en la capa activa de biblioteca+caché.
2. Eliminar artefactos legacy relacionales y comandos obsoletos.
3. Migrar layout en `biblioteca/` y ubicar contexto canónico por saga/cuento.
4. Limpiar documentación, rebranding global y trazabilidad de tarea.

## Decisiones

- Sin compatibilidad retroactiva para comandos legacy de CLI.
- Frontmatter en castellano, mapeo interno a identificadores en inglés.
- `referencia.pdf` como único nombre canónico de referencia.
- Contexto canónico movido a `biblioteca/` (`anclas.md` y páginas `NNN.md`).

## Cambios aplicados

- Código activo:
  - `app/config.py`, `app/__init__.py`, `app/routes.py`, `app/routes_v3.py`
  - `app/library_fs.py`, `app/library_cache.py`, `app/library_migration.py`
  - `app/text_pages.py`, `manage.py`
- Eliminaciones legacy:
  - `.markdownlint.json`
  - capa relacional legacy (`models`, `db`, `importer`)
  - `app/templates/saga.html`, `app/templates/libro.html`,
    `app/templates/anclas.html`
  - documentos contextuales redundantes de `docs/context/`
- Biblioteca:
  - migración aplicada a `meta.md` + `NNN.md` por cuento
  - creación de `biblioteca/nacidos-de-la-bruma-era-1/anclas.md`
  - normalización del nombre canónico `referencia.pdf`
  - creación de backups `origen_md.legacy.md`
- Documentación:
  - rebranding completo a “Generador de cuentos ilustrados”
  - limpieza de referencias obsoletas y normalización en castellano

## Validación ejecutada

- `python manage.py --help`
- `python manage.py migrate-library-layout --help`
- `python manage.py rebuild-cache --help`
- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py rebuild-cache`
- búsquedas globales de cadenas legacy y referencias obsoletas
- `python -m compileall app manage.py`

## Riesgos

- En este entorno, la caché puede operar en backend `:memory:` por permisos de
  escritura en disco.
- El archivo `era1_prompts_data.json` exigió borrado con permisos elevados.

## Seguimiento

1. Validar en tu entorno local que el backend de caché se materializa en
   `db/library_cache.sqlite`.
2. Ajustar metadatos editoriales de `meta.md` en cada cuento si hace falta.

## Commit asociado

- Mensaje de commit:
  `Tarea 005: inglés técnico, contexto en biblioteca y rebranding total`
- Hash de commit: `pendiente`
