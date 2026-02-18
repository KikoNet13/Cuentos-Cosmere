# TAREA-008-skill-revision-adaptacion-json-sin-sqlite

## Metadatos

- ID de tarea: `TAREA-008-skill-revision-adaptacion-json-sin-sqlite`
- Fecha: 13/02/26 13:20
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Refactorizar la app para usar `NN.json` como fuente de verdad sin SQLite ni CLI de ingesta, y reemplazar la skill operativa por `revision-orquestador-editorial`.

## Contexto

El flujo anterior dependia de `NN.md`, cache SQLite y comandos por batch (`inbox-parse`, `inbox-apply`), lo que aumentaba friccion para el trabajo editorial manual.

## Plan

1. Implementar dominio JSON (`story_store`) y catalogo por escaneo directo (`catalog_provider`).
2. Refactorizar rutas/UI a lectura y escritura sobre `NN.json`.
3. Retirar CLI de ingesta/cache y dejar `manage.py` solo con `runserver`.
4. Reemplazar skill global legacy por `revision-orquestador-editorial` y versionar skill en `.codex/skills`.
5. Actualizar ADR, documentacion operativa y trazabilidad repo.

## Decisiones

- Contrato canónico por cuento: `library/<book>/NN.json`.
- Runtime sin SQLite; lectura directa de disco con seam para índice futuro.
- Slots de imagen fijos: `main` obligatorio y `secondary` opcional.
- Alternativas de imagen con `active_id` y archivos opacos `img_<uuid>_<slug>.<ext>`.
- Edición web con guardado por página (`text.current`, `prompt.current`).
- Flujo de ingesta oficial en skill, no en comandos CLI.

## Cambios aplicados

- Runtime y dominio:
  - `app/story_store.py` (nuevo)
  - `app/catalog_provider.py` (nuevo)
  - `app/routes_v3.py` (refactor JSON sin cache)
  - `app/library_fs.py` (utilidades JSON)
  - `app/config.py` (sin `CACHE_DB_PATH`)
  - `manage.py` (solo `runserver`)
- UI:
  - `app/templates/base.html`
  - `app/templates/dashboard.html`
  - `app/templates/node.html`
  - `app/templates/cuento.html`
  - `app/static/css/app.css`
- Legacy retirado de flujo activo:
  - `app/library_cache.py` (stub de módulo retirado)
  - `app/notebooklm_ingest.py` (stub de módulo retirado)
- Skill:
  - `.codex/skills/revision-orquestador-editorial/SKILL.md`
  - `.codex/skills/revision-orquestador-editorial/references/checklist.md`
  - `.codex/skills/revision-orquestador-editorial/references/esquema-json.md`
  - `.codex/skills/revision-orquestador-editorial/references/revision-editorial.md`
  - instalacion global aplicada en `C:/Users/Kiko/.codex/skills/revision-orquestador-editorial`
  - skill legacy `notebooklm-ingest` retirada del scope global
- Documentacion:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/adr/0002-politica-sqlite-local.md`
  - `docs/adr/0004-biblioteca-fuente-verdad-cache-temporal.md`
  - `docs/adr/0007-canon-json-sin-sqlite-skill-editorial.md`
  - `docs/adr/INDICE.md`
  - `docs/tasks/TAREA-008-skill-revision-adaptacion-json-sin-sqlite.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

- `python manage.py --help`
- `python -c "from app import create_app; app=create_app(); print(app.url_map)"`
- `python -c "from app import create_app; c=create_app().test_client(); print(c.get('/health').status_code, c.get('/').status_code)"`
- `python -m compileall app manage.py` (fallo por permisos de escritura en `__pycache__` del entorno)
- `python -c "import ast,pathlib; ..."` sobre `manage.py` y `app/*.py` con `utf-8-sig` (ok)

## Riesgos

- Si existen cuentos JSON invalidos en `library/`, el catalogo los omite.
- La skill global requiere permisos fuera de workspace; en este entorno quedo instalada.

## Seguimiento

1. Ejecutar migracion real de `_inbox` a `NN.json` mediante la skill en una tarea operativa posterior.
2. Si el volumen crece, evaluar índice global JSON sin cambiar contrato de cuento.

## Commit asociado

- Mensaje de commit: `Tarea 008: skill revision-orquestador-editorial y runtime JSON sin SQLite`
- Hash de commit: pendiente

