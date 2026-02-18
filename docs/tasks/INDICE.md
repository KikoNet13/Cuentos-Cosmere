# Indice de tareas

- Proximo ID: `029`

## TAREA-028-flujo-guiado-relleno-imagenes

- Fecha: 18/02/26 17:12
- Estado: cerrada
- Resumen: flujo operativo unico `/_flow/image` para rellenar imagenes pendientes globales (anclas primero), con guardado por portapapeles y avance automatico al siguiente pendiente.
- Version: 2.5.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-028-flujo-guiado-relleno-imagenes.md`

## TAREA-027-modo-rapido-imagen-dossier-project-saga

- Fecha: 18/02/26 16:35
- Estado: cerrada
- Resumen: modo rapido en editor (copiar prompt/refs + pegar y guardar alternativa en un clic) y formalizacion del dossier `chatgpt_project_setup.md` por saga con refresh manual en `ingesta-cuentos`.
- Version: 2.4.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-027-modo-rapido-imagen-dossier-project-saga.md`

## TAREA-026-automatizacion-anclas-flujo-2-skills

- Fecha: 18/02/26 15:03
- Estado: cerrada
- Resumen: automatizacion de anclas en flujo 2 skills: `notebooklm-comunicacion` incorpora plan+meta/anclas y `ingesta-cuentos` enriquece `reference_ids` antes de importar, con soporte UTF-8 BOM.
- Version: 2.3.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-026-automatizacion-anclas-flujo-2-skills.md`

## TAREA-025-skill-notebooklm-fusion-ingesta

- Fecha: 18/02/26 15:35
- Estado: cerrada
- Resumen: nueva skill `notebooklm-comunicacion` para prompts por partes/fallback y extension de `ingesta-cuentos` para fusion en memoria + archivado `_processed`.
- Version: 2.2.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-025-skill-notebooklm-fusion-ingesta.md`

## TAREA-024-ejemplo-hansel-gretel-alineado-prompts-rutas-limpias

- Fecha: 18/02/26 10:05
- Estado: cerrada
- Resumen: ejemplo `hansel_y_gretel` realineado a nuevos recortes visuales, prompts operativos largos + anclas metadata-only, migracion breaking a rutas limpias y editor de portada separado por cuento.
- Version: 2.1.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-024-ejemplo-hansel-gretel-alineado-prompts-rutas-limpias.md`

## TAREA-023-giro-flujo-3-ias-ingesta-cuentos-contrato-nuevo-app

- Fecha: 17/02/26 18:03
- Estado: cerrada
- Resumen: giro al flujo 3 IAs con skill `ingesta-cuentos`, contrato nuevo `NN.json`/`meta.json`, refactor de app al esquema final y limpieza de `library` excepto `_inbox`.
- Version: 2.0.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-023-giro-flujo-3-ias-ingesta-cuentos-contrato-nuevo-app.md`

## TAREA-022-experimento-adaptacion-completa-pdf-unico-codex

- Fecha: 17/02/26 13:09
- Estado: cerrada
- Resumen: experimento editorial completo desde `El imperio final.pdf` (fuente canonica unica) a `el-imperio-final-codex`, con 8 cuentos de 16 paginas, sidecars de revision y biblia visual para imagegen.
- VersiÃ³n: 1.9.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-022-experimento-adaptacion-completa-pdf-unico-codex.md`

## TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts

- Fecha: 17/02/26 11:02
- Estado: cerrada
- Resumen: refactor de `adaptacion-ingesta-inicial` a skill 100% conversacional sin CLI/scripts, con contraste canonico por `pdf`, preguntas una a una y escritura incremental en archivos finales.
- VersiÃ³n: 1.8.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts.md`

## TAREA-020-contraste-canonico-obligatorio-pdf

- Fecha: 16/02/26 14:35
- Estado: cerrada
- Resumen: endurecida la skill de ingesta inicial con contraste canonico obligatorio contra PDF, gate de bloqueo por lote y contratos enriquecidos de contexto/issues/preguntas.
- VersiÃ³n: 1.7.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-020-contraste-canonico-obligatorio-pdf.md`

## TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest

- Fecha: 16/02/26 13:44
- Estado: cerrada
- Resumen: UI modular Jinja + Bulma + HTMX con navegacion por tarjetas, lectura/editor por rutas REST de pagina y compatibilidad legacy por redirect.
- VersiÃ³n: 1.6.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest.md`

## TAREA-018-skill-ingesta-inicial-interactiva

- Fecha: 16/02/26 12:49
- Estado: cerrada
- Resumen: skill de ingesta inicial interactiva para `_inbox` con salida `NN.json`, `adaptation_context.json` y `NN.issues.json`.
- VersiÃ³n: 1.5.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-018-skill-ingesta-inicial-interactiva.md`

## TAREA-017-limpieza-minima-runtime-repo

- Fecha: 16/02/26 11:31
- Estado: cerrada
- Resumen: limpieza de runtime al mÃ­nimo (sin mÃ³dulos legacy ni stubs retirados), dependencias reducidas y artefactos locales eliminados.
- VersiÃ³n: 1.4.1
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-017-limpieza-minima-runtime-repo.md`

## TAREA-015-reset-editorial-con-skills-sin-app

- Fecha: 16/02/26 10:51
- Estado: cerrada
- Resumen: reinicio editorial con frontera estricta `app` vs `skills`, nuevo stack `adaptacion-*` y sidecars `NN.review.json` + `NN.decisions.log.jsonl`.
- VersiÃ³n: 1.4.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-015-reset-editorial-con-skills-sin-app.md`

## TAREA-014-edad-objetivo-dinamica-inicio-adaptacion

- Fecha: 14/02/26 16:13
- Estado: cerrada
- Resumen: `target_age` pasa a ser obligatorio al inicio y persistido en `adaptation_profile.json`.
- VersiÃ³n: 1.3.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-014-edad-objetivo-dinamica-inicio-adaptacion.md`

## TAREA-013-contexto-review-ligera-glosario

- Fecha: 14/02/26 15:15
- Estado: cerrada
- Resumen: revisiÃ³n interactiva ligera de glosario con `context_review.json` y aplicaciÃ³n real en runtime editorial.
- VersiÃ³n: 1.2.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-013-contexto-review-ligera-glosario.md`

## TAREA-012-cascada-editorial-severidad-tres-skills

- Fecha: 13/02/26 18:40
- Estado: cerrada
- Resumen: cascada editorial por severidad con ciclo detecciÃ³n/decisiÃ³n/contraste para texto y prompts, contexto jerÃ¡rquico y nuevos sidecars.
- VersiÃ³n: 1.1.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-012-cascada-editorial-severidad-tres-skills.md`

## TAREA-011-orquestador-editorial-skills-ui-minimal

- Fecha: 13/02/26 16:24
- Estado: cerrada
- Resumen: pipeline editorial por skills encadenadas, sidecars `_reviews` y UI lectura/editor por modo.
- VersiÃ³n: 1.0.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-011-orquestador-editorial-skills-ui-minimal.md`

## TAREA-010-ingesta-editorial-el-imperio-final-json

- Fecha: 13/02/26 13:49
- Estado: cerrada
- Resumen: ingesta editorial de `El imperio final` a `NN.json` en `library/cosmere/.../el-imperio-final`.
- VersiÃ³n: 0.9.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-010-ingesta-editorial-el-imperio-final-json.md`

## TAREA-009-limpieza-library-el-imperio-final

- Fecha: 13/02/26 13:44
- Estado: cerrada
- Resumen: limpieza de `library/.../el-imperio-final` en remoto para reinicio editorial desde cero.
- VersiÃ³n: 0.8.1
- Commit: `pendiente`
- ADR relacionadas: (ninguna)
- Archivo: `docs/tasks/TAREA-009-limpieza-library-el-imperio-final.md`

## TAREA-008-skill-revision-adaptacion-json-sin-sqlite

- Fecha: 13/02/26 13:20
- Estado: cerrada
- Resumen: skill `revision-orquestador-editorial` y runtime JSON sin SQLite ni CLI de ingesta.
- VersiÃ³n: 0.8.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-008-skill-revision-adaptacion-json-sin-sqlite.md`

## TAREA-007-parser-ia-auditoria-terminologia

- Fecha: 12/02/26 22:29
- Estado: cerrada
- Resumen: parser con auditorÃ­a IA asistida, glosario jerÃ¡rquico y gate crÃ­tico mixto en apply.
- VersiÃ³n: 0.7.0
- Commit: `pendiente`
- ADR relacionadas: `0005`, `0006`
- Archivo: `docs/tasks/TAREA-007-parser-ia-auditoria-terminologia.md`

## TAREA-006-library-inbox-nnmd-skill-ingesta

- Fecha: 12/02/26 20:30
- Estado: cerrada
- Resumen: contrato `library/_inbox` + `NN.md`, migraciÃ³n de layout y skill de ingesta.
- VersiÃ³n: 0.6.0
- Commit: `pendiente`
- ADR relacionadas: `0004`, `0005`
- Archivo: `docs/tasks/TAREA-006-library-inbox-nnmd-skill-ingesta.md`

## TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding

- Fecha: 12/02/26 19:15
- Estado: cerrada
- Resumen: inglÃ©s tÃ©cnico, contexto canÃ³nico en biblioteca y rebranding total.
- VersiÃ³n: 0.5.0
- Commit: `pendiente`
- ADR relacionadas: `0003`, `0004`
- Archivo: `docs/tasks/TAREA-005-ingles-tecnico-contexto-biblioteca-rebranding.md`

## TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite

- Fecha: 12/02/26 17:20
- Estado: cerrada
- Resumen: biblioteca como fuente canÃ³nica y cachÃ© SQLite temporal.
- VersiÃ³n: 0.4.0
- Commit: `pendiente`
- ADR relacionadas: `0003`, `0004`
- Archivo: `docs/tasks/TAREA-004-refactor-db-biblioteca-canonica-cache-sqlite.md`

## TAREA-003-reestructuracion-pagina-ancla-imagen-ui

- Fecha: 12/02/26 14:41
- Estado: cerrada
- Resumen: reestructuraciÃ³n de dominio/UI orientada a generaciÃ³n visual.
- VersiÃ³n: 0.3.0
- Commit: `pendiente`
- ADR relacionadas: `0003`
- Archivo: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`

## TAREA-002-paginacion-adaptativa-archivo-importado

- Fecha: 12/02/26 14:00
- Estado: cerrada
- Resumen: paginaciÃ³n adaptativa por archivo importado.
- VersiÃ³n: 0.2.0
- Commit: `70c556a`
- ADR relacionadas: `0003`
- Archivo: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`

## TAREA-001-proyecto-profesional-contexto

- Fecha: 12/02/26 11:05
- Estado: cerrada
- Resumen: base de gobernanza, ADR y sistema documental inicial.
- VersiÃ³n: 0.1.0
- Commit: `52243f6`
- ADR relacionadas: `0001`, `0002`, `0003`
- Archivo: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`
