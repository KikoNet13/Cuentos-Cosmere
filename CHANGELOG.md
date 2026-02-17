# Registro de cambios

Registro breve de cambios relevantes.  
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [17/02/26] - Experimento de adaptacion completa desde PDF unico a version `-codex`

- Fuente canonica unica: `library/_inbox/El imperio final.pdf` (sin uso de internet).
- Segmentacion fija aplicada a 8 cuentos (`01..08`) con 16 paginas por cuento.
- Publicados `NN.json` con `status=definitive` en:
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/`
- Publicados sidecars por libro/cuento:
  - `adaptation_context.json`
  - `NN.issues.json`
  - `visual_bible.json` (nuevo sidecar de preparacion visual para imagegen).
- Prompts visuales detallados por pagina con continuidad de personajes, localizaciones y restricciones negativas.
- Tarea: `docs/tasks/TAREA-022-experimento-adaptacion-completa-pdf-unico-codex.md`.

## [17/02/26] - Skill de ingesta inicial 100% conversacional (sin scripts)

- Refactor de `.codex/skills/adaptacion-ingesta-inicial` a ejecucion en chat sin CLI ni `scripts/`.
- Eliminado el contrato de envelope ejecutable (`phase`, `pending_questions`, `planned_outputs`, `written_outputs`).
- `SKILL.md` reescrito con protocolo conversacional:
  - gate canonico bloqueante por lote;
  - preguntas una a una con opciones;
  - resolucion en bloque para la misma incoherencia repetida;
  - escritura incremental en archivos finales.
- Contraste canonico definido con skill `pdf` (sin OCR ni pipeline parser local en la skill).
- Contrato limpio en `references/contracts.md` centrado en salidas JSON y reglas operativas.
- Actualizada documentacion global (`AGENTS.md`, `README.md`, `app/README.md`, `docs/tasks/INDICE.md`).
- Tarea: `docs/tasks/TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts.md`.

## [16/02/26] - Ingesta inicial con contraste canonico obligatorio PDF

- `adaptacion-ingesta-inicial` bloquea por lote cuando falta cobertura canonica PDF (`input.missing_pdf`, `pdf.parser_unavailable`, `pdf.unreadable`).
- Nuevo preflight multi-backend de PDF (`pdfplumber` -> `pypdf`) en modo parser-only (sin OCR).
- Paginas no textuales del PDF (portada/mapa) pasan a ser no bloqueantes si hay senal narrativa suficiente para contraste.
- Contraste canonico refinado a alineacion semantica MD->PDF (sin comparacion 1:1 por numero de pagina).
- Glosario/contexto refinado a modo `md-first` con filtro de ruido y preguntas de glosario en `choice` con opciones.
- Contexto jerarquico por nodos (`book`, ancestros y global) con escalado a niveles superiores bajo confirmacion por termino.
- Nuevo detector de descriptores conceptuales para incoherencias tipo `Lord Legislador` vs `rey malvado` y variantes de entorno tipo `cae ceniza` vs `cae nieve gris`.
- Nuevos detectores por pagina: overlap canonico, entidades faltantes/sobrantes, diferencias numericas, perdida de citas y desajuste por edad (`age.too_complex|age.too_childish`).
- Contrato enriquecido:
  - `pending_questions[]` con `reason` y `evidence_pages`.
  - `NN.issues.json` con `review_mode`, `canon_source`, `metrics`, `source/detector/confidence`.
  - `adaptation_context.json` con `analysis_policy`, `canon_sources` y glosario extendido (`variants`, `source_presence`, `evidence_pages`).
- Documentacion operativa alineada en `AGENTS.md`, `README.md`, `app/README.md`.
- Tarea: `docs/tasks/TAREA-020-contraste-canonico-obligatorio-pdf.md`.

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
