# TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite

## Metadatos

- ID de tarea: `TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite`
- Fecha: 12/02/26 17:20
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0003`, `0004`

## Objetivo

Adoptar `biblioteca/` como fuente de verdad y SQLite solo como caché temporal
para navegación y lectura.

## Contexto

La app dependía de una capa relacional como verdad de negocio, duplicando
información narrativa ya presente en archivos Markdown.

## Plan

1. Crear capa de lectura canónica desde archivos.
2. Crear caché SQLite temporal con detección stale.
3. Añadir comandos CLI de migración de layout y refresco de caché.
4. Rehacer rutas/UI a navegación por árbol y cuento por página.

## Decisiones

- Contrato canónico: `meta.md` + `NNN.md`.
- Narrativa y prompts editables solo en archivos.
- Bloqueo de escritura de imágenes cuando la caché está stale.
- Fallback a caché en memoria si no hay escritura en disco.

## Cambios aplicados

- Módulos: `app/library_fs.py`, `app/library_cache.py`,
  `app/library_migration.py`.
- Rutas/UI de navegación de biblioteca y cuento por página.
- Comandos de CLI centrados en caché y migración de layout.
- Actualización documental asociada.

## Validación ejecutada

- `python manage.py --help`
- `python manage.py rebuild-cache --help`
- `python manage.py migrate-library-layout --help`
- `python manage.py migrate-library-layout --dry-run`
- `python manage.py rebuild-cache`

## Riesgos

- En este entorno, el backend SQLite en archivo puede caer a `:memory:`.
- Quedaba pendiente finalizar limpieza total de capa legacy y rebranding.

## Seguimiento

1. Completar transición sin compatibilidad de capa relacional legacy.
2. Consolidar contexto canónico dentro de `biblioteca/`.
3. Cerrar rebranding del producto y documentación histórica.

## Commit asociado

- Mensaje de commit: `Tarea 004: biblioteca canónica y caché temporal`
- Hash de commit: `pendiente`
