# Registro de cambios

Registro breve de cambios relevantes.  
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [16/02/26] - UI biblioteca Bulma + HTMX y rutas REST por pagina

- Rediseño UI de biblioteca con navegación por tarjetas tipo catálogo y miniaturas por cuento.
- Refactor backend web en módulos (`app/web/*`) y view-models compartidos.
- Nuevo contrato de rutas:
  - `/`
  - `/browse/<path>`
  - `/story/<path>/page/<int:page_number>`
  - `/editor/story/<path>/page/<int:page_number>`
  - `/fragments/story/<path>/page/<int:page_number>/*`
- HTMX en lectura para paginación parcial (`hx-push-url`) y panel avanzado ocultable.
- Activación de alternativas desde modo lectura con actualización parcial de panel y media.
- Integración Bulma y HTMX por CDN con fallback local en `app/static/vendor/`.
- Tarea: `docs/tasks/TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest.md`.

## [16/02/26] - Skill de ingesta inicial interactiva

- Nueva skill versionada en `.codex/skills/adaptacion-ingesta-inicial/` con CLI `run` para convertir `_inbox` a `NN.json` + sidecars de contexto/issues.
- Nuevo contrato de salida inicial:
  - `library/<book>/_reviews/adaptation_context.json`
  - `library/<book>/_reviews/NN.issues.json`
- Extendido `NN.json` con metadatos top-level de ingesta (`story_title`, `cover`, `source_refs`, `ingest_meta`).
- `app/story_store.py` actualizado para preservar esos metadatos y aceptar estados `in_review|definitive`.
- Tarea: `docs/tasks/TAREA-018-skill-ingesta-inicial-interactiva.md`.

## [16/02/26] - Limpieza minima de runtime y repositorio

- Eliminados modulos legacy/no usados de `app/` (migracion, stubs retirados y plantilla sin ruta activa).
- Simplificado `app/__init__.py` para importar blueprint directo desde `routes_v3`.
- Dependencias reducidas en `Pipfile` (se retiran `peewee` y `pypdf`) y lock regenerado.
- Documentacion operativa actualizada (`AGENTS.md`, `README.md`, `app/README.md`).
- Tarea: `docs/tasks/TAREA-017-limpieza-minima-runtime-repo.md`.

## [16/02/26] - Reset editorial con skills `adaptacion-*` fuera de `app`

- Se eliminaron skills legacy `revision-*` y la skill local `revision-adaptacion-editorial`.
- Se retiró `app/editorial_orquestador.py`.
- Se incorporó el stack:
  - `adaptacion-contexto`
  - `adaptacion-texto`
  - `adaptacion-prompts`
  - `adaptacion-cierre`
  - `adaptacion-orquestador`
- Nuevo contrato sidecar:
  - `library/<book>/_reviews/NN.review.json`
  - `library/<book>/_reviews/NN.decisions.log.jsonl`
- Documentación actualizada (`AGENTS.md`, `README.md`, `app/README.md`).
- Tarea: `docs/tasks/TAREA-015-reset-editorial-con-skills-sin-app.md`.

## [14/02/26] - Edad objetivo dinámica al iniciar adaptación

- `target_age` obligatorio al inicio del flujo.
- Tarea: `docs/tasks/TAREA-014-edad-objetivo-dinamica-inicio-adaptacion.md`.

## [14/02/26] - Revisión ligera de glosario en contexto canon

- Se añadió revisión manual de glosario y su sidecar.
- Tarea: `docs/tasks/TAREA-013-contexto-review-ligera-glosario.md`.

## [13/02/26] - Cascada editorial por severidad

- Flujo por severidad con ciclo detección/decisión/contraste.
- Tarea: `docs/tasks/TAREA-012-cascada-editorial-severidad-tres-skills.md`.

## [13/02/26] - Orquestador editorial por skills + UI mínima

- Pipeline editorial por skills encadenadas y sidecars de revisión.
- Tarea: `docs/tasks/TAREA-011-orquestador-editorial-skills-ui-minimal.md`.

## [13/02/26] - Ingesta editorial a `NN.json`

- Publicación de cuentos en contrato canónico JSON.
- Tarea: `docs/tasks/TAREA-010-ingesta-editorial-el-imperio-final-json.md`.

## [13/02/26] - Limpieza de biblioteca para reinicio editorial

- Limpieza de layout legacy de `library`.
- Tarea: `docs/tasks/TAREA-009-limpieza-library-el-imperio-final.md`.

## [13/02/26] - Skill editorial y runtime JSON sin SQLite

- Adopción de `NN.json` como contrato de runtime.
- Tarea: `docs/tasks/TAREA-008-skill-revision-adaptacion-json-sin-sqlite.md`.

## [12/02/26] - Parser IA asistida y gate crítico mixto

- Auditoría asistida, glosario jerárquico y gate crítico.
- Tarea: `docs/tasks/TAREA-007-parser-ia-auditoria-terminologia.md`.

## [12/02/26] - `library/_inbox` + contrato `NN.md`

- Flujo de ingesta con contrato plano por cuento.
- Tarea: `docs/tasks/TAREA-006-library-inbox-nnmd-skill-ingesta.md`.

## [12/02/26] - Rebranding técnico y contexto canónico

- Actualización de nomenclatura y estructura de contexto.
- Tarea: `docs/tasks/TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding.md`.

## [12/02/26] - Refactor biblioteca canónica y cache SQLite temporal

- Reorganización de fuente canónica y soporte temporal de cache.
- Tarea: `docs/tasks/TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite.md`.

## [12/02/26] - Reestructuración UI y dominio de página

- Reordenación de UI orientada a generación visual.
- Tarea: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`.

## [12/02/26] - Paginación adaptativa

- Implementación de paginación adaptativa por archivo importado.
- Tarea: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`.

## [12/02/26] - Base documental y gobernanza

- Sistema inicial de operación, ADR y tareas.
- Tarea: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`.
