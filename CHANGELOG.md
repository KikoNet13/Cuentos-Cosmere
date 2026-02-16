# Registro de cambios

Registro breve de cambios relevantes.
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [14/02/26] - Edad objetivo dinámica al iniciar adaptación

- Se añadió sidecar por libro `adaptation_profile.json` en `library/<book_rel_path>/_reviews/`.
- Nueva API `run_contexto_adaptation_profile(...)` para persistir/actualizar `target_age` y umbrales base.
- `run_orquestador_editorial(...)` ahora acepta `target_age` opcional y detiene en `phase=awaiting_target_age` si no existe edad en input ni en perfil.
- Se añadió `run_orquestador_editorial_resume(...)` con el mismo gate de edad.
- `run_contexto_canon(...)` ahora expone `adaptation_profile` y `adaptation_profile_rel`.
- Skills y documentación actualizadas para exigir confirmación de edad objetivo al inicio.
- Tarea: `docs/tasks/TAREA-014-edad-objetivo-dinamica-inicio-adaptacion.md`.

## [14/02/26] - Revisión ligera de glosario en contexto canon

- Se añadió sidecar opcional `context_review.json` en `library/<book_rel_path>/_reviews/` para decisiones editoriales de terminología.
- Se incorporó `run_contexto_revision_glosario(...)` en `app/editorial_orquestador.py` para persistir decisiones y recalcular `glossary_merged.json` efectivo.
- `run_contexto_canon(...)` ahora aplica automáticamente `context_review.json` cuando existe y conserva comportamiento previo cuando no existe.
- Los hallazgos `glossary_forbidden_term` ahora proponen sustitución usando `replacement_target` (alias preferido o canónico).
- Se actualizó la documentación de skills y guías para explicitar:
  - revisión ligera manual desde `revision-contexto-canon`
  - consumo pasivo por `revision-orquestador-editorial` (sin disparo automático).
- Se incluyen cambios de preparación de entorno en `library/.../el-imperio-final` para pruebas desde cero.
- Tarea: `docs/tasks/TAREA-013-contexto-review-ligera-glosario.md`.

## [13/02/26] - Cascada editorial por severidad con ciclo de 3 skills

- Se amplió `app/editorial_orquestador.py` con cascada por severidad (`critical -> major -> minor -> info`) para etapas de texto y prompts.
- Se incorporó contexto jerárquico con salida en:
  - `library/<book_rel_path>/_reviews/context_chain.json`
  - `library/<book_rel_path>/_reviews/glossary_merged.json`
- Por cuento se añadieron sidecars de ejecución:
  - `NN.findings.json`
  - `NN.choices.json`
  - `NN.contrast.json`
  - `NN.passes.json`
- `pipeline_state.json` ahora expone:
  - `stage`
  - `severity_band`
  - `pass_index`
  - `convergence_status`
  - `alerts_open`
- Se actualizó la guía de uso y la documentación operativa para el flujo de cascada.
- Tarea: `docs/tasks/TAREA-012-cascada-editorial-severidad-tres-skills.md`.

## [13/02/26] - Pipeline orquestador editorial por skills + UI de lectura minimal

- Se implementó `app/editorial_orquestador.py` con:
  - descubrimiento de inbox recursivo con exclusión `_ignore`
  - prioridad de duplicados `NN.md` por raíz
  - ingesta a `NN.json`
  - auditoría/corrección de texto y prompts con gate por `critical|major`
  - sidecars de revisión en `_reviews` (`NN.review.json|md`, `NN.decisions.json`, `pipeline_state.json`)
  - ciclo de estado editorial: `draft`, `text_reviewed|text_blocked`, `prompt_reviewed|prompt_blocked`, `ready`.
- La webapp ahora usa vista de lectura por defecto y modo editorial con `?editor=1`.
- Se agregó set de skills encadenadas:
  - `revision-ingesta-json`
  - `revision-auditoria-texto`
  - `revision-correccion-texto`
  - `revision-auditoria-prompts`
  - `revision-correccion-prompts`
  - `revision-orquestador-editorial`
- `revision-orquestador-editorial` queda como skill operativa única del flujo orquestado.
- Tarea: `docs/tasks/TAREA-011-orquestador-editorial-skills-ui-minimal.md`.

## [13/02/26] - Ingesta editorial de El imperio final a JSON canónico

- Se procesaron las propuestas `01-05.md` de `library/_inbox/El imperio final` (incluyendo `_future`).
- Se crearon `01.json` a `05.json` en `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final`.
- Cada cuento quedó con 16 páginas en contrato canónico: `text.original/current`, `images.main.prompt.original/current`, `active_id`, `alternatives`.
- Tarea: `docs/tasks/TAREA-010-ingesta-editorial-el-imperio-final-json.md`.

## [13/02/26] - Limpieza de library para reinicio editorial

- Se eliminaron de `library/nacidos-de-la-bruma-era-1/el-imperio-final` los archivos legacy `NN.md` y `NN.pdf`.
- Se eliminó `library/nacidos-de-la-bruma-era-1/anclas.md` como parte de la limpieza inicial.
- La ingesta/editorial posterior queda delegada a la skill `revision-orquestador-editorial`.
- Tarea: `docs/tasks/TAREA-009-limpieza-library-el-imperio-final.md`.

## [13/02/26] - Skill editorial + runtime JSON sin SQLite

- Se adoptó `library/.../NN.json` como contrato canónico de runtime.
- Se retiró SQLite de navegación/lectura y se eliminó flujo CLI de ingesta por batch.
- La webapp ahora opera por escaneo directo de disco con:
  - comparativa `original/current`
  - guardado por pagina
  - alternativas de imagen por slot y `active_id`.
- `manage.py` queda solo con `runserver`.
- Se reemplazó la skill global legacy por `revision-orquestador-editorial`.
- ADR: `docs/adr/0007-canon-json-sin-sqlite-skill-editorial.md`.
- Tarea: `docs/tasks/TAREA-008-skill-revision-adaptacion-json-sin-sqlite.md`.

## [12/02/26] - Parser IA asistida + gate crítico mixto

- `inbox-parse` ahora genera `ai_context.json`, `review_ai.md` y `review_ai.json` por batch.
- Se agrego `inbox-review-validate` para validar esquema y consistencia de `review_ai.json`.
- `inbox-apply` ahora bloquea por `status` pendiente/bloqueado y por `critical_open > 0`.
- `inbox-apply --force` ahora exige `--force-reason` y registra trazabilidad de override en `manifest.json`.
- Se formalizó glosario jerárquico por nodo en `meta.md` (`## Glosario`).
- ADR: `docs/adr/0006-parser-ia-asistida-gate-critico.md`.
- Tarea: `docs/tasks/TAREA-007-parser-ia-auditoria-terminologia.md`.

## [12/02/26] - Library + inbox + cuento `NN.md`

- Se completó el renombre canónico de datos a `library/`.
- Se implemento ingesta por lotes en `library/_inbox` con comandos:
  - `inbox-parse`
  - `inbox-apply --approve`
- Se consolidó el contrato de cuento en archivo único `NN.md` con cabeceras de `Meta`, `Texto`, `Prompts` y `Requisitos`.
- Se aplicó migración de layout legacy a formato plano de libro (`NN.md` + `NN.pdf`).
- Se añadió ADR `0005` para formalizar el nuevo contrato.
- Se creó skill global `notebooklm-ingest` para flujo parsear/revisar/aplicar.
- Tarea: `docs/tasks/TAREA-006-library-inbox-nnmd-skill-ingesta.md`.

## [12/02/26] - Inglés técnico + contexto en biblioteca + rebranding

- Se consolidó el código activo con identificadores técnicos en inglés.
- Se retiró la capa relacional legacy y comandos CLI obsoletos.
- Se migró `biblioteca/` al contrato `meta.md` + `NNN.md`.
- Se creó guía de anclas por saga en `biblioteca/nacidos-de-la-bruma-era-1/anclas.md`.
- Se fijó `referencia.pdf` como nombre canónico de PDF de referencia.
- Se completo el rebranding visible a **Generador de cuentos ilustrados**.
- Tarea: `docs/tasks/TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding.md`.

## [12/02/26] - Biblioteca canónica + caché temporal

- Se adopto `biblioteca/` como fuente de verdad de narrativa y prompts.
- Se añadió caché SQLite temporal con detección stale por fingerprint global.
- Se incorporaron comandos `migrate-library-layout` y `rebuild-cache`.
- Se rehizo la UI a navegación por árbol genérico y vista por página.
- Tarea: `docs/tasks/TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite.md`.

## [12/02/26] - Reestructuración de dominio/UI

- Se introdujo un dominio orientado a pagina y generacion visual.
- Se rehizo la UI de cuento para navegación y trabajo por página.
- Se reforzo la trazabilidad documental de la transicion.
- Tarea: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`.

## [12/02/26] - Paginación adaptativa por archivo importado

- Se eliminó la expectativa fija de páginas en importación y UI.
- El total de páginas pasó a depender del archivo importado.
- Tarea: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`.

## [12/02/26] - Base de gobernanza

- Se definió gobernanza del repositorio y su trazabilidad.
- Se incorporo sistema de ADR y tareas con indice dedicado.
- Tarea: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`.
