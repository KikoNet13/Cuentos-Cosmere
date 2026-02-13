# Registro de cambios

Registro breve de cambios relevantes.
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [13/02/26] - Limpieza de library para reinicio editorial

- Se eliminaron de `library/nacidos-de-la-bruma-era-1/el-imperio-final` los archivos legacy `NN.md` y `NN.pdf`.
- Se elimino `library/nacidos-de-la-bruma-era-1/anclas.md` como parte de la limpieza inicial.
- La ingesta/editorial posterior queda delegada a la skill `revision-adaptacion-editorial`.
- Tarea: `docs/tasks/TAREA-009-limpieza-library-el-imperio-final.md`.

## [13/02/26] - Skill editorial + runtime JSON sin SQLite

- Se adopto `library/.../NN.json` como contrato canonico de runtime.
- Se retiro SQLite de navegacion/lectura y se elimino flujo CLI de ingesta por batch.
- La webapp ahora opera por escaneo directo de disco con:
  - comparativa `original/current`
  - guardado por pagina
  - alternativas de imagen por slot y `active_id`.
- `manage.py` queda solo con `runserver`.
- Se reemplazo la skill global legacy por `revision-adaptacion-editorial`.
- ADR: `docs/adr/0007-canon-json-sin-sqlite-skill-editorial.md`.
- Tarea: `docs/tasks/TAREA-008-skill-revision-adaptacion-json-sin-sqlite.md`.

## [12/02/26] - Parser IA asistida + gate critico mixto

- `inbox-parse` ahora genera `ai_context.json`, `review_ai.md` y `review_ai.json` por batch.
- Se agrego `inbox-review-validate` para validar esquema y consistencia de `review_ai.json`.
- `inbox-apply` ahora bloquea por `status` pendiente/bloqueado y por `critical_open > 0`.
- `inbox-apply --force` ahora exige `--force-reason` y registra trazabilidad de override en `manifest.json`.
- Se formalizo glosario jerarquico por nodo en `meta.md` (`## Glosario`).
- ADR: `docs/adr/0006-parser-ia-asistida-gate-critico.md`.
- Tarea: `docs/tasks/TAREA-007-parser-ia-auditoria-terminologia.md`.

## [12/02/26] - Library + inbox + cuento `NN.md`

- Se completo el renombre canonico de datos a `library/`.
- Se implemento ingesta por lotes en `library/_inbox` con comandos:
  - `inbox-parse`
  - `inbox-apply --approve`
- Se consolido el contrato de cuento en archivo unico `NN.md` con cabeceras de `Meta`, `Texto`, `Prompts` y `Requisitos`.
- Se aplico migracion de layout legacy a formato plano de libro (`NN.md` + `NN.pdf`).
- Se anadio ADR `0005` para formalizar el nuevo contrato.
- Se creo skill global `notebooklm-ingest` para flujo parsear/revisar/aplicar.
- Tarea: `docs/tasks/TAREA-006-library-inbox-nnmd-skill-ingesta.md`.

## [12/02/26] - Ingles tecnico + contexto en biblioteca + rebranding

- Se consolido el codigo activo con identificadores tecnicos en ingles.
- Se retiro la capa relacional legacy y comandos CLI obsoletos.
- Se migro `biblioteca/` al contrato `meta.md` + `NNN.md`.
- Se creo guia de anclas por saga en `biblioteca/nacidos-de-la-bruma-era-1/anclas.md`.
- Se fijo `referencia.pdf` como nombre canonico de PDF de referencia.
- Se completo el rebranding visible a **Generador de cuentos ilustrados**.
- Tarea: `docs/tasks/TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding.md`.

## [12/02/26] - Biblioteca canonica + cache temporal

- Se adopto `biblioteca/` como fuente de verdad de narrativa y prompts.
- Se anadio cache SQLite temporal con deteccion stale por fingerprint global.
- Se incorporaron comandos `migrate-library-layout` y `rebuild-cache`.
- Se rehizo la UI a navegacion por arbol generico y vista por pagina.
- Tarea: `docs/tasks/TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite.md`.

## [12/02/26] - Reestructuracion de dominio/UI

- Se introdujo un dominio orientado a pagina y generacion visual.
- Se rehizo la UI de cuento para navegacion y trabajo por pagina.
- Se reforzo la trazabilidad documental de la transicion.
- Tarea: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`.

## [12/02/26] - Paginacion adaptativa por archivo importado

- Se elimino la expectativa fija de paginas en importacion y UI.
- El total de paginas paso a depender del archivo importado.
- Tarea: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`.

## [12/02/26] - Base de gobernanza

- Se definio gobernanza del repositorio y su trazabilidad.
- Se incorporo sistema de ADR y tareas con indice dedicado.
- Tarea: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`.
