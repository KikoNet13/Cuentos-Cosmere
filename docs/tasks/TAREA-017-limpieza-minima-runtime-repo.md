# TAREA-017-limpieza-minima-runtime-repo

## Metadatos

- ID de tarea: `TAREA-017-limpieza-minima-runtime-repo`
- Fecha: 16/02/26 11:31
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Reducir el repositorio al minimo operativo actual, eliminando codigo legacy/no usado y artefactos locales de cache/SQLite.

## Contexto

- El runtime vigente usa Flask + lectura directa de `library/` via `NN.json`.
- Seguian presentes modulos legacy de migracion, stubs retirados y una plantilla sin ruta activa.
- Habia dependencias de Python no usadas (`peewee`, `pypdf`) y archivos locales de cache/SQLite.

## Plan

1. Auditar referencias reales del runtime (`manage.py`, `app/__init__.py`, `routes_v3`, `story_store`, `catalog_provider`).
2. Eliminar modulos y plantillas sin referencias activas.
3. Reducir dependencias en `Pipfile` y regenerar `Pipfile.lock`.
4. Limpiar artefactos locales no versionados y validar runtime con comandos finitos.

## Decisiones

- Se elimina codigo no referenciado por el runtime actual:
  - `app/library_fs.py`
  - `app/library_migration.py`
  - `app/text_pages.py`
  - `app/utils.py`
  - `app/library_cache.py`
  - `app/notebooklm_ingest.py`
  - `app/routes.py`
  - `app/templates/cuento.html`
- `app/__init__.py` pasa a importar `web_bp` desde `app/routes_v3.py` directamente.
- Se actualiza documentacion operativa para reflejar que no hay skills de adaptacion versionadas en este repo.
- Se retiran dependencias no usadas (`peewee`, `pypdf`).
- `.venv/` no pudo eliminarse por bloqueo de `python.exe` (WinError 5); se mantiene ignorada.

## Cambios aplicados

- Codigo y plantillas:
  - `app/__init__.py`
  - eliminados: `app/library_fs.py`, `app/library_migration.py`, `app/text_pages.py`, `app/utils.py`
  - eliminados: `app/library_cache.py`, `app/notebooklm_ingest.py`, `app/routes.py`
  - eliminado: `app/templates/cuento.html`
- Dependencias:
  - `Pipfile`
  - `Pipfile.lock`
- Documentacion:
  - `README.md`
  - `app/README.md`
  - `AGENTS.md`
  - `docs/tasks/TAREA-017-limpieza-minima-runtime-repo.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`
- Limpieza local (no versionada):
  - eliminados `db/`, `cache_test.sqlite*`, `cache_write_probe_root.txt`, `__pycache__/`, `app/__pycache__/`

## Validacion ejecutada

1. `rg -n` de referencias cruzadas para confirmar modulos no usados.
2. `python -m compileall app manage.py`
   - OK, sin errores.
3. `python -c "from app import create_app; app=create_app(); print(sorted(str(r) for r in app.url_map.iter_rules()))"`
   - OK, rutas esperadas disponibles.
4. `python -c "from app import create_app; c=create_app().test_client(); print(c.get('/health').status_code, c.get('/').status_code)"`
   - OK, respuesta `200 200`.
5. `pipenv lock` (forzando venv fuera del proyecto)
   - OK, `Pipfile.lock` regenerado.

## Riesgos

- Si algun flujo externo importaba explicitamente los modulos eliminados, requerira ajuste.
- `.venv/` quedo sin limpiar por bloqueo de archivo en Windows.

## Seguimiento

1. Opcional: cerrar procesos que bloqueen `.venv/Scripts/python.exe` y borrar `.venv/` para limpieza total local.
2. Opcional: documentar retroactivamente `TAREA-016` en `docs/tasks/` para mantener continuidad historica en indice.

## Commit asociado

- Mensaje de commit: `Tarea 017: limpieza minima del repositorio`
- Hash de commit: pendiente
