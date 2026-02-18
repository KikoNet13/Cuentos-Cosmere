# Registro de cambios

Registro breve de cambios relevantes.  
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [18/02/26] - Automatizacion de anclas en flujo 2 skills

- `notebooklm-comunicacion` ampliada a flujo oficial en 4 fases:
  - plan de coleccion,
  - `meta.json` con anclas y reglas,
  - partes de cuentos (`NN_a/NN_b` + fallback `a1/a2/b1/b2`),
  - deltas por archivo.
- Nueva convencion operativa de anclas y referencias:
  - IDs por categoria (`style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`),
  - `reference_ids` basados en `meta.anchors[].image_filenames`.
- `ingesta-cuentos` actualizada con enriquecimiento preimport de `reference_ids`:
  - conserva refs existentes,
  - autocompleta faltantes con anclas de estilo + semantica,
  - warnings de cobertura (`refs.autofilled`, `refs.style_only_fallback`, `refs.anchor_missing`).
- Contrato de ingesta alineado con compatibilidad de entrada JSON en UTF-8 y UTF-8 BOM.
- Documentacion de orquestacion actualizada en `AGENTS.md` y `docs/guia-orquestador-editorial.md`.
- Tarea: `docs/tasks/TAREA-026-automatizacion-anclas-flujo-2-skills.md`.

## [18/02/26] - Skill NotebookLM + fusion por partes en ingesta

- Nueva skill `.codex/skills/notebooklm-comunicacion/` (conversacional, sin scripts) para preparar prompts por partes:
  - `NN_a`/`NN_b` (8+8),
  - fallback automatico `NN_a1/a2` + `NN_b1/b2` (4+4),
  - mensajes delta por archivo para reentregas NotebookLM.
- `ingesta-cuentos` ampliada para aceptar partes en `_inbox`, fusionarlas en memoria por cuento y validar el contrato final antes de importar.
- Contrato de referencia extendido con reglas de fusion, rangos por sufijo y nuevos codigos de error/warning (`input.pending_notebooklm`, `merge.*`).
- Archivado post-import definido en `library/_processed/<book_title>/<timestamp>/` cuando el lote se completa sin pendientes.
- Documentacion alineada en `AGENTS.md`, `README.md` y `docs/guia-orquestador-editorial.md`.
- Tarea: `docs/tasks/TAREA-025-skill-notebooklm-fusion-ingesta.md`.

## [18/02/26] - Ejemplo Hansel/Gretel alineado + prompts operativos + rutas limpias

- `library/hansel_y_gretel/01.json` y espejo `hansel_y_gretel.json` realineados al set visual nuevo (`style_refs` recortado sin texto en imagen).
- Sustituidos assets activos (cover + paginas 1..15), eliminados no usados y regenerado `library/hansel_y_gretel/images/index.json` solo con activos.
- Nueva pagina 16 sin imagen:
  - `images.main.status = not_required`
  - `active_id = \"\"`
  - `alternatives = []`
- Prompts de portada y paginas reescritos como prompts largos de generacion para ChatGPT Image, con estructura fija y `reference_ids` simulados por anclas.
- Nuevo `library/hansel_y_gretel/meta.json` con `collection.title`, `anchors[]`, `updated_at` (anclas metadata-only sin archivos reales).
- Migracion breaking de rutas web:
  - canonica `GET /<path_rel>`
  - fragmentos `/<story_path>/_fr/*`
  - acciones `/<story_path>/_act/*`
  - eliminadas rutas legacy `/browse/*`, `/story/*`, `/editor/story/*`, `/n/*` (sin redirect).
- UI:
  - portada retirada de lectura por pagina y editor por pagina;
  - nuevo editor de portada en `?editor=1` sin `p`.
- Tarea: `docs/tasks/TAREA-024-ejemplo-hansel-gretel-alineado-prompts-rutas-limpias.md`.

## [17/02/26] - Giro a flujo 3 IAs + skill `ingesta-cuentos` + contrato nuevo app

- Sustituida la skill `adaptacion-ingesta-inicial` por `ingesta-cuentos` (conversacional, sin scripts).
- Nuevo contrato operativo:
  - `NN.json` simplificado (`text`/`prompt` string, `cover` como slot completo).
  - `meta.json` jerarquico por nodo (`global + ancestros + libro`).
  - imagenes por nodo en `images/` con indice `images/index.json`.
- Refactor fuerte de runtime en `app/`:
  - `story_store` reescrito al formato nuevo;
  - soporte de portada editable como slot;
  - soporte de referencias `reference_ids[]` con warning de faltantes;
  - panel de anclas/meta en editor con alternativas e imagen activa por nivel.
- Gobernanza/documentacion alineada a flujo 3 IAs:
  - `AGENTS.md`, `README.md`, `app/README.md`.
- Reseteo de `library` para pruebas reales, preservando solo `_inbox`.
- Tarea: `docs/tasks/TAREA-023-giro-flujo-3-ias-ingesta-cuentos-contrato-nuevo-app.md`.

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

- RediseÃ±o UI de biblioteca con navegaciÃ³n por tarjetas tipo catÃ¡logo y miniaturas por cuento.
- Refactor backend web en mÃ³dulos (`app/web/*`) y view-models compartidos.
- Nuevo contrato de rutas:
  - `/`
  - `/browse/<path>`
  - `/story/<path>/page/<int:page_number>`
  - `/editor/story/<path>/page/<int:page_number>`
  - `/fragments/story/<path>/page/<int:page_number>/*`
- HTMX en lectura para paginaciÃ³n parcial (`hx-push-url`) y panel avanzado ocultable.
- ActivaciÃ³n de alternativas desde modo lectura con actualizaciÃ³n parcial de panel y media.
- IntegraciÃ³n Bulma y HTMX por CDN con fallback local en `app/static/vendor/`.
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
- Se retirÃ³ `app/editorial_orquestador.py`.
- Se incorporÃ³ el stack:
  - `adaptacion-contexto`
  - `adaptacion-texto`
  - `adaptacion-prompts`
  - `adaptacion-cierre`
  - `adaptacion-orquestador`
- Nuevo contrato sidecar:
  - `library/<book>/_reviews/NN.review.json`
  - `library/<book>/_reviews/NN.decisions.log.jsonl`
- DocumentaciÃ³n actualizada (`AGENTS.md`, `README.md`, `app/README.md`).
- Tarea: `docs/tasks/TAREA-015-reset-editorial-con-skills-sin-app.md`.

## [14/02/26] - Edad objetivo dinÃ¡mica al iniciar adaptaciÃ³n

- `target_age` obligatorio al inicio del flujo.
- Tarea: `docs/tasks/TAREA-014-edad-objetivo-dinamica-inicio-adaptacion.md`.

## [14/02/26] - RevisiÃ³n ligera de glosario en contexto canon

- Se aÃ±adiÃ³ revisiÃ³n manual de glosario y su sidecar.
- Tarea: `docs/tasks/TAREA-013-contexto-review-ligera-glosario.md`.

## [13/02/26] - Cascada editorial por severidad

- Flujo por severidad con ciclo detecciÃ³n/decisiÃ³n/contraste.
- Tarea: `docs/tasks/TAREA-012-cascada-editorial-severidad-tres-skills.md`.

## [13/02/26] - Orquestador editorial por skills + UI mÃ­nima

- Pipeline editorial por skills encadenadas y sidecars de revisiÃ³n.
- Tarea: `docs/tasks/TAREA-011-orquestador-editorial-skills-ui-minimal.md`.

## [13/02/26] - Ingesta editorial a `NN.json`

- PublicaciÃ³n de cuentos en contrato canÃ³nico JSON.
- Tarea: `docs/tasks/TAREA-010-ingesta-editorial-el-imperio-final-json.md`.

## [13/02/26] - Limpieza de biblioteca para reinicio editorial

- Limpieza de layout legacy de `library`.
- Tarea: `docs/tasks/TAREA-009-limpieza-library-el-imperio-final.md`.

## [13/02/26] - Skill editorial y runtime JSON sin SQLite

- AdopciÃ³n de `NN.json` como contrato de runtime.
- Tarea: `docs/tasks/TAREA-008-skill-revision-adaptacion-json-sin-sqlite.md`.

## [12/02/26] - Parser IA asistida y gate crÃ­tico mixto

- AuditorÃ­a asistida, glosario jerÃ¡rquico y gate crÃ­tico.
- Tarea: `docs/tasks/TAREA-007-parser-ia-auditoria-terminologia.md`.

## [12/02/26] - `library/_inbox` + contrato `NN.md`

- Flujo de ingesta con contrato plano por cuento.
- Tarea: `docs/tasks/TAREA-006-library-inbox-nnmd-skill-ingesta.md`.

## [12/02/26] - Rebranding tÃ©cnico y contexto canÃ³nico

- ActualizaciÃ³n de nomenclatura y estructura de contexto.
- Tarea: `docs/tasks/TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding.md`.

## [12/02/26] - Refactor biblioteca canÃ³nica y cache SQLite temporal

- ReorganizaciÃ³n de fuente canÃ³nica y soporte temporal de cache.
- Tarea: `docs/tasks/TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite.md`.

## [12/02/26] - ReestructuraciÃ³n UI y dominio de pÃ¡gina

- ReordenaciÃ³n de UI orientada a generaciÃ³n visual.
- Tarea: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`.

## [12/02/26] - PaginaciÃ³n adaptativa

- ImplementaciÃ³n de paginaciÃ³n adaptativa por archivo importado.
- Tarea: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`.

## [12/02/26] - Base documental y gobernanza

- Sistema inicial de operaciÃ³n, ADR y tareas.
- Tarea: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`.
