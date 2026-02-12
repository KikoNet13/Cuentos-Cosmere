# Registro de cambios

Registro breve de cambios relevantes.
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [12/02/26] - Library + inbox + cuento `NN.md`

- Se completó el renombre canónico de datos a `library/`.
- Se implementó ingestión por lotes en `library/_inbox` con comandos:
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
- Se completó el rebranding visible a **Generador de cuentos ilustrados**.
- Tarea: `docs/tasks/TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding.md`.

## [12/02/26] - Biblioteca canónica + caché temporal

- Se adoptó `biblioteca/` como fuente de verdad de narrativa y prompts.
- Se añadió caché SQLite temporal con detección stale por fingerprint global.
- Se incorporaron comandos `migrate-library-layout` y `rebuild-cache`.
- Se rehízo la UI a navegación por árbol genérico y vista por página.
- Tarea: `docs/tasks/TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite.md`.

## [12/02/26] - Reestructuración de dominio/UI

- Se introdujo un dominio orientado a página y generación visual.
- Se rehízo la UI de cuento para navegación y trabajo por página.
- Se reforzó la trazabilidad documental de la transición.
- Tarea: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`.

## [12/02/26] - Paginación adaptativa por archivo importado

- Se eliminó la expectativa fija de páginas en importación y UI.
- El total de páginas pasó a depender del archivo importado.
- Tarea: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`.

## [12/02/26] - Base de gobernanza

- Se definió gobernanza del repositorio y su trazabilidad.
- Se incorporó sistema de ADR y tareas con índice dedicado.
- Tarea: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`.
