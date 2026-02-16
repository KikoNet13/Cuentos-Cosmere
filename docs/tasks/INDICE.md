# Índice de tareas

- Próximo ID: `020`

## TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest

- Fecha: 16/02/26 13:44
- Estado: cerrada
- Resumen: UI modular Jinja + Bulma + HTMX con navegacion por tarjetas, lectura/editor por rutas REST de pagina y compatibilidad legacy por redirect.
- Versión: 1.6.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest.md`

## TAREA-018-skill-ingesta-inicial-interactiva

- Fecha: 16/02/26 12:49
- Estado: cerrada
- Resumen: skill de ingesta inicial interactiva para `_inbox` con salida `NN.json`, `adaptation_context.json` y `NN.issues.json`.
- Versión: 1.5.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-018-skill-ingesta-inicial-interactiva.md`

## TAREA-017-limpieza-minima-runtime-repo

- Fecha: 16/02/26 11:31
- Estado: cerrada
- Resumen: limpieza de runtime al mínimo (sin módulos legacy ni stubs retirados), dependencias reducidas y artefactos locales eliminados.
- Versión: 1.4.1
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-017-limpieza-minima-runtime-repo.md`

## TAREA-015-reset-editorial-con-skills-sin-app

- Fecha: 16/02/26 10:51
- Estado: cerrada
- Resumen: reinicio editorial con frontera estricta `app` vs `skills`, nuevo stack `adaptacion-*` y sidecars `NN.review.json` + `NN.decisions.log.jsonl`.
- Versión: 1.4.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-015-reset-editorial-con-skills-sin-app.md`

## TAREA-014-edad-objetivo-dinamica-inicio-adaptacion

- Fecha: 14/02/26 16:13
- Estado: cerrada
- Resumen: `target_age` pasa a ser obligatorio al inicio y persistido en `adaptation_profile.json`.
- Versión: 1.3.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-014-edad-objetivo-dinamica-inicio-adaptacion.md`

## TAREA-013-contexto-review-ligera-glosario

- Fecha: 14/02/26 15:15
- Estado: cerrada
- Resumen: revisión interactiva ligera de glosario con `context_review.json` y aplicación real en runtime editorial.
- Versión: 1.2.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-013-contexto-review-ligera-glosario.md`

## TAREA-012-cascada-editorial-severidad-tres-skills

- Fecha: 13/02/26 18:40
- Estado: cerrada
- Resumen: cascada editorial por severidad con ciclo detección/decisión/contraste para texto y prompts, contexto jerárquico y nuevos sidecars.
- Versión: 1.1.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-012-cascada-editorial-severidad-tres-skills.md`

## TAREA-011-orquestador-editorial-skills-ui-minimal

- Fecha: 13/02/26 16:24
- Estado: cerrada
- Resumen: pipeline editorial por skills encadenadas, sidecars `_reviews` y UI lectura/editor por modo.
- Versión: 1.0.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-011-orquestador-editorial-skills-ui-minimal.md`

## TAREA-010-ingesta-editorial-el-imperio-final-json

- Fecha: 13/02/26 13:49
- Estado: cerrada
- Resumen: ingesta editorial de `El imperio final` a `NN.json` en `library/cosmere/.../el-imperio-final`.
- Versión: 0.9.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-010-ingesta-editorial-el-imperio-final-json.md`

## TAREA-009-limpieza-library-el-imperio-final

- Fecha: 13/02/26 13:44
- Estado: cerrada
- Resumen: limpieza de `library/.../el-imperio-final` en remoto para reinicio editorial desde cero.
- Versión: 0.8.1
- Commit: `pendiente`
- ADR relacionadas: (ninguna)
- Archivo: `docs/tasks/TAREA-009-limpieza-library-el-imperio-final.md`

## TAREA-008-skill-revision-adaptacion-json-sin-sqlite

- Fecha: 13/02/26 13:20
- Estado: cerrada
- Resumen: skill `revision-orquestador-editorial` y runtime JSON sin SQLite ni CLI de ingesta.
- Versión: 0.8.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-008-skill-revision-adaptacion-json-sin-sqlite.md`

## TAREA-007-parser-ia-auditoria-terminologia

- Fecha: 12/02/26 22:29
- Estado: cerrada
- Resumen: parser con auditoría IA asistida, glosario jerárquico y gate crítico mixto en apply.
- Versión: 0.7.0
- Commit: `pendiente`
- ADR relacionadas: `0005`, `0006`
- Archivo: `docs/tasks/TAREA-007-parser-ia-auditoria-terminologia.md`

## TAREA-006-library-inbox-nnmd-skill-ingesta

- Fecha: 12/02/26 20:30
- Estado: cerrada
- Resumen: contrato `library/_inbox` + `NN.md`, migración de layout y skill de ingesta.
- Versión: 0.6.0
- Commit: `pendiente`
- ADR relacionadas: `0004`, `0005`
- Archivo: `docs/tasks/TAREA-006-library-inbox-nnmd-skill-ingesta.md`

## TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding

- Fecha: 12/02/26 19:15
- Estado: cerrada
- Resumen: inglés técnico, contexto canónico en biblioteca y rebranding total.
- Versión: 0.5.0
- Commit: `pendiente`
- ADR relacionadas: `0003`, `0004`
- Archivo: `docs/tasks/TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding.md`

## TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite

- Fecha: 12/02/26 17:20
- Estado: cerrada
- Resumen: biblioteca como fuente canónica y caché SQLite temporal.
- Versión: 0.4.0
- Commit: `pendiente`
- ADR relacionadas: `0003`, `0004`
- Archivo: `docs/tasks/TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite.md`

## TAREA-003-reestructuracion-pagina-ancla-imagen-ui

- Fecha: 12/02/26 14:41
- Estado: cerrada
- Resumen: reestructuración de dominio/UI orientada a generación visual.
- Versión: 0.3.0
- Commit: `pendiente`
- ADR relacionadas: `0003`
- Archivo: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`

## TAREA-002-paginacion-adaptativa-archivo-importado

- Fecha: 12/02/26 14:00
- Estado: cerrada
- Resumen: paginación adaptativa por archivo importado.
- Versión: 0.2.0
- Commit: `70c556a`
- ADR relacionadas: `0003`
- Archivo: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`

## TAREA-001-proyecto-profesional-contexto

- Fecha: 12/02/26 11:05
- Estado: cerrada
- Resumen: base de gobernanza, ADR y sistema documental inicial.
- Versión: 0.1.0
- Commit: `52243f6`
- ADR relacionadas: `0001`, `0002`, `0003`
- Archivo: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`
