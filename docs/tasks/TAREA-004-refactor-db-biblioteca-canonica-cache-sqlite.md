# TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite

## Metadatos

- ID de tarea: `TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite`
- Fecha: 12/02/26 17:20
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0003`, `0004`

## Objetivo

Replantear persistencia para usar `biblioteca/` como fuente de verdad y
SQLite solo como caché temporal de navegación/lectura.

## Contexto

La app dependía del modelo relacional como verdad de negocio. Eso duplicaba
la información narrativa/prompts respecto a los archivos Markdown y obligaba a
sincronizaciones frágiles.

## Plan

1. Crear capa de lectura canónica desde archivos (`library_fs`).
2. Crear caché SQLite temporal con fingerprint global y detección stale.
3. Añadir comandos CLI para `rebuild-cache` y migración de layout legacy.
4. Rehacer rutas/UI para navegación por árbol y cuento por página.
5. Registrar trazabilidad documental de la decisión.

## Decisiones

- Contrato canónico de cuento: `meta.md` + páginas `NNN.md`.
- Texto y prompts solo se editan en archivos.
- La UI no edita narrativa/prompts; solo copia y guarda imágenes por slot.
- Bloqueo de escritura cuando la caché está stale.
- Fallback a SQLite en memoria si el backend de archivo no es escribible.

## Cambios aplicados

- Nuevos módulos:
  - `app/library_fs.py`
  - `app/library_cache.py`
  - `app/library_migration.py`
- CLI:
  - `manage.py` (comandos `rebuild-cache`, `migrate-library-layout`,
    `import` como alias deprecado)
- Web/UI:
  - `app/routes_v3.py`
  - `app/templates/base.html`
  - `app/templates/dashboard.html`
  - `app/templates/node.html`
  - `app/templates/cuento.html`
  - `app/static/css/app.css`
- Config y bootstrap:
  - `app/config.py`
  - `app/__init__.py`
- Documentación:
  - `README.md`
  - `app/README.md`
  - `AGENTS.md`
  - `docs/adr/INDICE.md`
  - `docs/adr/0003-contrato-importacion-respaldo.md`
  - `docs/adr/0004-biblioteca-fuente-verdad-cache-temporal.md`
  - `docs/context/INDICE.md`
  - `docs/context/prompts_imagenes_master_era1.md`
  - `docs/context/canon_cuento_objetivo_16_paginas.md`
- Higiene local:
  - `.gitignore` actualizado para SQLite temporal y probes locales.

## Validación ejecutada

- `python manage.py --help`
- `python manage.py rebuild-cache --help`
- `python manage.py migrate-library-layout --help`
- `python manage.py migrate-library-layout --dry-run`
- `python manage.py rebuild-cache`
- Validación de sintaxis AST en módulos Python tocados.

## Riesgos

- En este entorno, SQLite en archivo falla con `disk I/O error`; se activa
  fallback `:memory:` (no persistente entre procesos).
- Hasta ejecutar migración `--apply`, la caché no detectará cuentos porque el
  layout legacy aún usa `origen_md.md`.
- Queda trabajo pendiente para retirar completamente comandos/modelos legacy.

## Seguimiento

1. Ejecutar `python manage.py migrate-library-layout --apply` en entorno local
   con permisos de escritura normales.
2. Reejecutar `python manage.py rebuild-cache` y validar navegación completa.
3. Definir fecha de retiro de comandos legacy (`migrate-models-v3`,
   `export-prompts`, `import-prompts`).

## Commit asociado

- Mensaje de commit: `Tarea 004: biblioteca canónica y caché temporal`
- Hash de commit: `pendiente`
