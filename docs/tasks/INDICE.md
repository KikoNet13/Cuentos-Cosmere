# índice de tareas

- Proximo ID: `039`
## TAREA-038-fix-request-entity-too-large-pegar-guardar

- Fecha: 19/02/26 00:50
- Estado: cerrada
- Resumen: correccion de `413 Request Entity Too Large` en acciones de "Pegar y guardar" mediante envio multipart (`image_file`) y limites backend de 20 MB.
- Version: 2.7.8
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-038-fix-request-entity-too-large-pegar-guardar.md`

## TAREA-037-meta-prompts-y-flow-exclusion-underscore

- Fecha: 19/02/26 01:00
- Estado: cerrada
- Resumen: copia de `meta_prompts.json` a `library/los_juegos_del_hambre/meta.json` y ajuste de `/_flow/image` para excluir rutas con carpetas que empiezan por `_`.
- Version: 2.7.7
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-037-meta-prompts-y-flow-exclusion-underscore.md`

## TAREA-036-copiar-prompts-inbox-a-biblioteca-los-juegos

- Fecha: 19/02/26 00:32
- Estado: cerrada
- Resumen: copia de `cover_prompt` y `page_prompts[].main_prompt` desde `library/_inbox/Los juegos del hambre/NN_prompts.json` hacia `library/los_juegos_del_hambre/NN.json`, sincronizando `updated_at`.
- Versi?n: 2.7.6
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-036-copiar-prompts-inbox-a-biblioteca-los-juegos.md`

## TAREA-035-normalizacion-utf8-acentos-json-md

- Fecha: 18/02/26 23:05
- Estado: cerrada
- Resumen: normalización global de archivos `.md/.json` versionados a UTF-8 sin BOM, reparación de mojibake y corrección integral de acentos/ñ en texto natural con salvaguardas sobre bloques de código/backticks.
- Versión: 2.7.5
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-035-normalizacion-utf8-acentos-json-md.md`

## TAREA-034-ajuste-placeholders-nb-meta-largo-fuente-sin-prompts-anchor

- Fecha: 18/02/26 22:25
- Estado: cerrada
- Resumen: ajuste de placeholders para NotebookLM: `meta_prompts.json` exige prompts largos estructurados para anchors y la fuente NB elimina prompts de anchors para dejar solo ids/nombres/filenames + textos narrativos.
- Versión: 2.7.4
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-034-ajuste-placeholders-nb-meta-largo-fuente-sin-prompts-anchor.md`

## TAREA-033-fuente-nb-unica-textos-anchors-regen-placeholders

- Fecha: 18/02/26 22:16
- Estado: cerrada
- Resumen: se crea fuente única `.md` para NotebookLM con textos+anchors y se regeneran `01..11_prompts.json` + `meta_prompts.json` para referenciarla, sin depender de rutas/webapp.
- Versión: 2.7.3
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-033-fuente-nb-unica-textos-anchors-regen-placeholders.md`

## TAREA-032-placeholders-nn-prompts-con-texto-de-paginas

- Fecha: 18/02/26 22:11
- Estado: cerrada
- Resumen: actualización de `01..11_prompts.json` para incluir texto base completo por página dentro de cada placeholder, de forma que NotebookLM no dependa de conocer previamente las páginas adaptadas.
- Versión: 2.7.2
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-032-placeholders-nn-prompts-con-texto-de-paginas.md`

## TAREA-031-contexto-notebooklm-placeholders-meta-anchors

- Fecha: 18/02/26 22:08
- Estado: cerrada
- Resumen: ajuste de placeholders `NN_prompts.json` para NotebookLM sin dependencias de rutas/webapp y alta de `meta_prompts.json` para generar `meta.json` con anchors.
- Versión: 2.7.1
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-031-contexto-notebooklm-placeholders-meta-anchors.md`

## TAREA-030-placeholders-nn-prompts-notebooklm-orquestador

- Fecha: 18/02/26 22:00
- Estado: cerrada
- Resumen: parche de orquestacion con placeholders `01_prompts.json..11_prompts.json` en `library/_inbox/Los juegos del hambre/`, listos para copy/paste con salida estricta de NotebookLM en JSON puro.
- Versión: 2.7.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-030-placeholders-nn-prompts-notebooklm-orquestador.md`

## TAREA-029-style-prompt-maestro-chatgpt-project

- Fecha: 18/02/26 21:50
- Estado: cerrada
- Resumen: incorporacion de `Style Prompt Maestro` canónico (EN + resumen ES), politica de composición por intencion del slot (`full-bleed`/`spot art`) y sincronizacion de guia operativa + plantilla oficial de dossier ChatGPT Project.
- Versión: 2.6.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-029-style-prompt-maestro-chatgpt-project.md`

## TAREA-028-flujo-guiado-relleno-imagenes

- Fecha: 18/02/26 17:12
- Estado: cerrada
- Resumen: flujo operativo único `/_flow/image` para rellenar imágenes pendientes globales (anclas primero), con guardado por portapapeles y avance automático al siguiente pendiente.
- Versión: 2.5.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-028-flujo-guiado-relleno-imagenes.md`

## TAREA-027-modo-rapido-imagen-dossier-project-saga

- Fecha: 18/02/26 16:35
- Estado: cerrada
- Resumen: modo rapido en editor (copiar prompt/refs + pegar y guardar alternativa en un clic) y formalizacion del dossier `chatgpt_project_setup.md` por saga con refresh manual en `ingesta-cuentos`.
- Versión: 2.4.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-027-modo-rapido-imagen-dossier-project-saga.md`

## TAREA-026-automatizacion-anclas-flujo-2-skills

- Fecha: 18/02/26 15:03
- Estado: cerrada
- Resumen: automatizacion de anclas en flujo 2 skills: `notebooklm-comunicacion` incorpora plan+meta/anclas y `ingesta-cuentos` enriquece `reference_ids` antes de importar, con soporte UTF-8 BOM.
- Versión: 2.3.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-026-automatizacion-anclas-flujo-2-skills.md`

## TAREA-025-skill-notebooklm-fusion-ingesta

- Fecha: 18/02/26 15:35
- Estado: cerrada
- Resumen: nueva skill `notebooklm-comunicacion` para prompts por partes/fallback y extension de `ingesta-cuentos` para fusion en memoria + archivado `_processed`.
- Versión: 2.2.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-025-skill-notebooklm-fusion-ingesta.md`

## TAREA-024-ejemplo-hansel-gretel-alineado-prompts-rutas-limpias

- Fecha: 18/02/26 10:05
- Estado: cerrada
- Resumen: ejemplo `hansel_y_gretel` realineado a nuevos recortes visuales, prompts operativos largos + anclas metadata-only, migracion breaking a rutas limpias y editor de portada separado por cuento.
- Versión: 2.1.0
- Commit: `pendiente`
- ADR relacionadas: `0008`
- Archivo: `docs/tasks/TAREA-024-ejemplo-hansel-gretel-alineado-prompts-rutas-limpias.md`

## TAREA-023-giro-flujo-3-ias-ingesta-cuentos-contrato-nuevo-app

- Fecha: 17/02/26 18:03
- Estado: cerrada
- Resumen: giro al flujo 3 IAs con skill `ingesta-cuentos`, contrato nuevo `NN.json`/`meta.json`, refactor de app al esquema final y limpieza de `library` excepto `_inbox`.
- Versión: 2.0.0
- Commit: `pendiente`
- ADR relacionadas: `0007`, `0008`
- Archivo: `docs/tasks/TAREA-023-giro-flujo-3-ias-ingesta-cuentos-contrato-nuevo-app.md`

## TAREA-022-experimento-adaptacion-completa-pdf-unico-codex

- Fecha: 17/02/26 13:09
- Estado: cerrada
- Resumen: experimento editorial completo desde `El imperio final.pdf` (fuente canónica única) a `el-imperio-final-codex`, con 8 cuentos de 16 páginas, sidecars de revisión y biblia visual para imagegen.
- Versión: 1.9.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-022-experimento-adaptacion-completa-pdf-unico-codex.md`

## TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts

- Fecha: 17/02/26 11:02
- Estado: cerrada
- Resumen: refactor de `adaptacion-ingesta-inicial` a skill 100% conversacional sin CLI/scripts, con contraste canónico por `pdf`, preguntas una a una y escritura incremental en archivos finales.
- Versión: 1.8.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts.md`

## TAREA-020-contraste-canonico-obligatorio-pdf

- Fecha: 16/02/26 14:35
- Estado: cerrada
- Resumen: endurecida la skill de ingesta inicial con contraste canónico obligatorio contra PDF, gate de bloqueo por lote y contratos enriquecidos de contexto/issues/preguntas.
- Versión: 1.7.0
- Commit: `pendiente`
- ADR relacionadas: `0007`
- Archivo: `docs/tasks/TAREA-020-contraste-canonico-obligatorio-pdf.md`

## TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest

- Fecha: 16/02/26 13:44
- Estado: cerrada
- Resumen: UI modular Jinja + Bulma + HTMX con navegación por tarjetas, lectura/editor por rutas REST de página y compatibilidad legacy por redirect.
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
