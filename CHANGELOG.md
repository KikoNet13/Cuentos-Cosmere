# Registro de cambios

Registro breve de cambios relevantes.  
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [19/02/26] - Fix 413 en "Pegar y guardar" (multipart + limites 20 MB)

- Se corrige el error `Request Entity Too Large` en acciones de pegado rapido de imagen.
- Backend:
  - `app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024`
  - `app.config["MAX_FORM_MEMORY_SIZE"] = 20 * 1024 * 1024`
  - manejo explicito de `RequestEntityTooLarge` con flash y redireccion.
- Frontend (`app/static/js/clipboard.js`):
  - `pasteImageAndSubmit(...)` ahora envia imagen pegada como `image_file` via `FormData`.
  - elimina `pasted_image_data` del envio principal y mantiene fallback legacy.
- Compatibilidad: `extract_image_payload` conserva soporte de `image_file` y fallback base64.
- Tarea: `docs/tasks/TAREA-038-fix-request-entity-too-large-pegar-guardar.md`.

## [19/02/26] - Meta prompts aplicados y exclusiones `_` en flujo de pendientes

- Se copia `library/_inbox/Los juegos del hambre/meta_prompts.json` sobre `library/los_juegos_del_hambre/meta.json`.
- Quedan aplicados en meta de saga los prompts largos de anchors, `style_rules`, `continuity_rules` y `updated_at` entregados por NB.
- Se ajusta `app/web/image_flow.py`:
  - `/_flow/image` ahora excluye cualquier ruta que contenga carpetas cuyo nombre empiece por `_`.
- Validaciones:
  - `META_MATCH=True` entre origen y destino de meta.
  - `BAD_UNDERSCORE_ITEMS=0` en cola pendiente.
- Tarea: `docs/tasks/TAREA-037-meta-prompts-y-flow-exclusion-underscore.md`.

## [19/02/26] - Copia de prompts de `_inbox` a biblioteca (`los_juegos_del_hambre`)

- Se copian prompts de `01..11_prompts.json` hacia `library/los_juegos_del_hambre/01..11.json`.
- Campos sincronizados por cuento:
  - `cover.prompt` desde `cover_prompt`.
  - `pages[].images.main.prompt` desde `page_prompts[].main_prompt`.
  - `updated_at` del cuento desde el `_prompts.json`.
- Se preserva el resto de campos (`text`, `reference_ids`, `alternatives`, `active_id`, `status`).
- Validaci?n de consistencia de copia: `COPIED_OK=11`.
- Tarea: `docs/tasks/TAREA-036-copiar-prompts-inbox-a-biblioteca-los-juegos.md`.

## [18/02/26] - Normalización UTF-8 y acentos en `.md/.json` versionados

- Se normalizan todos los `.md/.json` versionados a UTF-8 sin BOM.
- Se corrige mojibake residual y acentuación en español (texto natural) con salvaguardas en bloques de código y texto entre backticks.
- Validación final:
  - `BAD_UTF8=0`
  - `WITH_BOM=0`
  - `WITH_REPL=0`
  - `MOJIBAKE_FILES=0`
- No se tocan archivos no versionados.
- Tarea: `docs/tasks/TAREA-035-normalizacion-utf8-acentos-json-md.md`.

## [18/02/26] - Ajuste final NB: meta con prompts largos y fuente sin prompts de anchors

- Se actualiza `library/_inbox/Los juegos del hambre/meta_prompts.json` para exigir prompts largos estructurados tambien en `anchors[].prompt`:
  - 8 bloques obligatorios en orden,
  - rango objetivo 700-1500 caracteres,
  - uso de IDs canónicos en `REFERENCIAS (reference_ids)`.
- Se limpia `library/_inbox/Los juegos del hambre/FUENTE_NB_los_juegos_textos_y_anchors.md`:
  - se eliminan prompts de anchors,
  - se mantienen `id`, `name`, `image_filenames` y los textos narrativos por cuento/pagina.
- No se modifica `library/los_juegos_del_hambre/NN.json`.
- Tarea: `docs/tasks/TAREA-034-ajuste-placeholders-nb-meta-largo-fuente-sin-prompts-anchor.md`.

## [18/02/26] - Fuente NB única con textos y anchors + regen de placeholders

- Se crea fuente central para NotebookLM:
  - `library/_inbox/Los juegos del hambre/FUENTE_NB_los_juegos_textos_y_anchors.md`.
- La fuente incluye:
  - anchors canónicos del meta (`id`, `name`, `prompt`, `image_filenames`),
  - textos completos por cuento y página (`01..11`).
- Se regeneran `01..11_prompts.json` para referenciar esa fuente nueva:
  - prompts más cortos para copy/paste,
  - sin dependencia de rutas locales ni webapp,
  - salida estricta en JSON puro.
- Se actualiza `meta_prompts.json`:
  - exige inclusion de TODOS los anchors canónicos,
  - incluye listado explicito de IDs obligatorios.
- Validacion automática:
  - fuente presente,
  - 11 placeholders referenciando la fuente,
  - reglas de salida estricta y meta completas (`NB_SOURCE_AND_PLACEHOLDERS_OK`).
- No se restauran backups ni se modifica `NN.json`.
- Tarea: `docs/tasks/TAREA-033-fuente-nb-unica-textos-anchors-regen-placeholders.md`.

## [18/02/26] - Placeholders con texto de páginas para NotebookLM

- Se actualizan `01..11_prompts.json` en `library/_inbox/Los juegos del hambre/` para incluir el texto narrativo completo por página.
- Nuevo bloque en cada placeholder:
  - `TEXTO BASE DEL CUENTO (USAR COMO FUENTE NARRATIVA PARA PAGE_PROMPTS)`,
  - con lista `page_number` + `text` para todas las páginas.
- Reglas reforzadas:
  - no inventar ni cambiar el orden de páginas,
  - priorizar el texto base del bloque ante dudas.
- Se mantiene salida estricta para NB:
  - solo JSON válido,
  - sin markdown ni explicaciones,
  - sin texto fuera del JSON final.
- Validacion automática:
  - 11 placeholders con bloque de texto base detectado (`PAGE_TEXT_SECTION_OK`).
- No se restauran backups ni se modifica `NN.json`.
- Tarea: `docs/tasks/TAREA-032-placeholders-nn-prompts-con-texto-de-paginas.md`.

## [18/02/26] - Contexto NotebookLM en placeholders + meta anchors

- Se corrigen los placeholders `01..11_prompts.json` para operar en NotebookLM sin depender de rutas/ficheros locales ni de la webapp.
- Se agrega bloque explicito de contexto disponible en NB:
  - libros canónicos,
  - ejemplo Hansel y Gretel,
  - fuente de estilo ya cargada.
- Se ajusta la instruccion de referencias:
  - usar anchors del `meta.json` (`style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`).
- Se crea placeholder faltante:
  - `library/_inbox/Los juegos del hambre/meta_prompts.json`,
  - para pedir a NB el `meta.json` completo con anchors y reglas.
- Validacion automática:
  - 11 placeholders de cuentos detectados con patron correcto,
  - clausulas de salida estricta presentes,
  - `meta_prompts.json` presente y consistente.
- No se restauran backups ni se modifica `NN.json` en este ajuste.
- Tarea: `docs/tasks/TAREA-031-contexto-notebooklm-placeholders-meta-anchors.md`.

## [18/02/26] - Placeholders `NN_prompts.json` para pedir prompts completos a NotebookLM

- Se crea parche de orquestacion para `Los juegos del hambre`:
  - nuevos placeholders en `library/_inbox/Los juegos del hambre/`:
    - `01_prompts.json` ... `11_prompts.json`.
- Cada placeholder queda en texto plano (listo para copy/paste) con reglas estrictas de salida para NB:
  - `Devuelve SOLO JSON valido`,
  - sin markdown ni explicaciones,
  - sin texto fuera del JSON,
  - salida exactamente igual al contenido final del `NN_prompts.json` correspondiente.
- Schema requerido en salida NB por cuento:
  - `story_id`, `title`, `book_rel_path`, `updated_at`, `cover_prompt`, `page_prompts[]`, `secondary_prompts[]` opcional.
- Validacion local aplicada:
  - 11 archivos detectados con patron `^\\d{2}_prompts\\.json$`,
  - placeholders con clausulas obligatorias de salida estricta.
- No se restauran backups ni se modifica `NN.json` en esta tarea.
- Tarea: `docs/tasks/TAREA-030-placeholders-nn-prompts-notebooklm-orquestador.md`.

## [18/02/26] - Style Prompt Maestro en setup ChatGPT Project (Los juegos del hambre)

- Se incorpora bloque `STYLE PROMPT MAESTRO (CANONICO)` en setup de saga actual:
  - prompt EN literal,
  - resumen técnico ES breve,
  - regla explicita de reutilizacion por turno.
- Se formaliza politica de composición por intencion del slot:
  - `full-bleed` y `spot art` solo cuando el slot/prompt lo solicita;
  - sin regla fija por paridad.
- Se alinea la guia operativa `PASOS_OPERATIVOS.md` con verificacion obligatoria del style prompt y checklist de QA técnico de estilo.
- Se sincroniza plantilla oficial de dossier y bloque B2 de `ingesta-cuentos` con el nuevo estándar.
- Tarea: `docs/tasks/TAREA-029-style-prompt-maestro-chatgpt-project.md`.

## [18/02/26] - Flujo guiado de imágenes pendientes (anclas primero)

- Nuevo modo operativo global en webapp:
  - `GET /_flow/image` muestra solo el primer pendiente de imagen.
  - `POST /_flow/image/submit` guarda desde portapapeles y avanza al siguiente pendiente.
- Cola global de pendientes con prioridad:
  - primero anclas de `meta.json`,
  - luego cuentos (`cover -> main -> secondary`) por `story_rel_path`.
- Criterio de pendiente:
  - slot/ancla sin imagen activa válida en disco.
  - se excluyen elementos `not_required` y los que tienen prompt vacio (reportados aparte).
- Boton en topbar:
  - "Rellenar imágenes pendientes" con badge de pendientes cuando aplica.
- Reuso de logica de decodificacion:
  - helper comun `app/web/image_upload.py` compartido entre editor tradicional y flujo guiado.
- Nueva vista dedicada:
  - `app/templates/story/flow/image_fill.html` con acciones minimas de produccion:
    - copiar prompt,
    - copiar refs individuales,
    - pegar y guardar.
- Tarea: `docs/tasks/TAREA-028-flujo-guiado-relleno-imagenes.md`.

## [18/02/26] - Modo rapido de imagen + dossier ChatGPT Project por saga

- UI de editor reforzada con barra `Modo rapido` en slots y portada:
  - copiar prompt,
  - copiar referencias individuales,
  - acción `Pegar y guardar alternativa` en un clic.
- `clipboard.js` ampliado con `pasteImageAndSubmit(...)`:
  - lee imagen del portapapeles,
  - carga hidden input,
  - envia formulario automaticamente,
  - mantiene fallback manual con mensajes de error claros.
- Estilos nuevos en `app/static/css/pages.css` para ergonomia de acciones rapidas.
- `ingesta-cuentos` ampliada a nivel de skill/contrato para dossier operativo por saga:
  - generar/regenerar `library/<book_rel_path>/chatgpt_project_setup.md` tras ingesta válida,
  - soporte de refresh manual del dossier sin reimport.
- Documentacion de orquestacion actualizada:
  - `AGENTS.md`,
  - `README.md`,
  - `docs/guia-orquestador-editorial.md`.
- Tarea: `docs/tasks/TAREA-027-modo-rapido-imagen-dossier-project-saga.md`.

## [18/02/26] - Automatizacion de anclas en flujo 2 skills

- `notebooklm-comunicacion` ampliada a flujo oficial en 4 fases:
  - plan de colección,
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
  - fallback automático `NN_a1/a2` + `NN_b1/b2` (4+4),
  - mensajes delta por archivo para reentregas NotebookLM.
- `ingesta-cuentos` ampliada para aceptar partes en `_inbox`, fusionarlas en memoria por cuento y validar el contrato final antes de importar.
- Contrato de referencia extendido con reglas de fusion, rangos por sufijo y nuevos codigos de error/warning (`input.pending_notebooklm`, `merge.*`).
- Archivado post-import definido en `library/_processed/<book_title>/<timestamp>/` cuando el lote se completa sin pendientes.
- Documentacion alineada en `AGENTS.md`, `README.md` y `docs/guia-orquestador-editorial.md`.
- Tarea: `docs/tasks/TAREA-025-skill-notebooklm-fusion-ingesta.md`.

## [18/02/26] - Ejemplo Hansel/Gretel alineado + prompts operativos + rutas limpias

- `library/hansel_y_gretel/01.json` y espejo `hansel_y_gretel.json` realineados al set visual nuevo (`style_refs` recortado sin texto en imagen).
- Sustituidos assets activos (cover + páginas 1..15), eliminados no usados y regenerado `library/hansel_y_gretel/images/index.json` solo con activos.
- Nueva página 16 sin imagen:
  - `images.main.status = not_required`
  - `active_id = \"\"`
  - `alternatives = []`
- Prompts de portada y páginas reescritos como prompts largos de generación para ChatGPT Image, con estructura fija y `reference_ids` simulados por anclas.
- Nuevo `library/hansel_y_gretel/meta.json` con `collection.title`, `anchors[]`, `updated_at` (anclas metadata-only sin archivos reales).
- Migracion breaking de rutas web:
  - canónica `GET /<path_rel>`
  - fragmentos `/<story_path>/_fr/*`
  - acciones `/<story_path>/_act/*`
  - eliminadas rutas legacy `/browse/*`, `/story/*`, `/editor/story/*`, `/n/*` (sin redirect).
- UI:
  - portada retirada de lectura por página y editor por página;
  - nuevo editor de portada en `?editor=1` sin `p`.
- Tarea: `docs/tasks/TAREA-024-ejemplo-hansel-gretel-alineado-prompts-rutas-limpias.md`.

## [17/02/26] - Giro a flujo 3 IAs + skill `ingesta-cuentos` + contrato nuevo app

- Sustituida la skill `adaptacion-ingesta-inicial` por `ingesta-cuentos` (conversacional, sin scripts).
- Nuevo contrato operativo:
  - `NN.json` simplificado (`text`/`prompt` string, `cover` como slot completo).
  - `meta.json` jerarquico por nodo (`global + ancestros + libro`).
  - imágenes por nodo en `images/` con índice `images/index.json`.
- Refactor fuerte de runtime en `app/`:
  - `story_store` reescrito al formato nuevo;
  - soporte de portada editable como slot;
  - soporte de referencias `reference_ids[]` con warning de faltantes;
  - panel de anclas/meta en editor con alternativas e imagen activa por nivel.
- Gobernanza/documentacion alineada a flujo 3 IAs:
  - `AGENTS.md`, `README.md`, `app/README.md`.
- Reseteo de `library` para pruebas reales, preservando solo `_inbox`.
- Tarea: `docs/tasks/TAREA-023-giro-flujo-3-ias-ingesta-cuentos-contrato-nuevo-app.md`.

## [17/02/26] - Experimento de adaptación completa desde PDF único a versión `-codex`

- Fuente canónica única: `library/_inbox/El imperio final.pdf` (sin uso de internet).
- Segmentacion fija aplicada a 8 cuentos (`01..08`) con 16 páginas por cuento.
- Publicados `NN.json` con `status=definitive` en:
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/`
- Publicados sidecars por libro/cuento:
  - `adaptation_context.json`
  - `NN.issues.json`
  - `visual_bible.json` (nuevo sidecar de preparacion visual para imagegen).
- Prompts visuales detallados por página con continuidad de personajes, localizaciones y restricciones negativas.
- Tarea: `docs/tasks/TAREA-022-experimento-adaptacion-completa-pdf-unico-codex.md`.

## [17/02/26] - Skill de ingesta inicial 100% conversacional (sin scripts)

- Refactor de `.codex/skills/adaptacion-ingesta-inicial` a ejecucion en chat sin CLI ni `scripts/`.
- Eliminado el contrato de envelope ejecutable (`phase`, `pending_questions`, `planned_outputs`, `written_outputs`).
- `SKILL.md` reescrito con protocolo conversacional:
  - gate canónico bloqueante por lote;
  - preguntas una a una con opciones;
  - resolucion en bloque para la misma incoherencia repetida;
  - escritura incremental en archivos finales.
- Contraste canónico definido con skill `pdf` (sin OCR ni pipeline parser local en la skill).
- Contrato limpio en `references/contracts.md` centrado en salidas JSON y reglas operativas.
- Actualizada documentacion global (`AGENTS.md`, `README.md`, `app/README.md`, `docs/tasks/INDICE.md`).
- Tarea: `docs/tasks/TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts.md`.

## [16/02/26] - Ingesta inicial con contraste canónico obligatorio PDF

- `adaptacion-ingesta-inicial` bloquea por lote cuando falta cobertura canónica PDF (`input.missing_pdf`, `pdf.parser_unavailable`, `pdf.unreadable`).
- Nuevo preflight multi-backend de PDF (`pdfplumber` -> `pypdf`) en modo parser-only (sin OCR).
- Páginas no textuales del PDF (portada/mapa) pasan a ser no bloqueantes si hay senal narrativa suficiente para contraste.
- Contraste canónico refinado a alineacion semantica MD->PDF (sin comparacion 1:1 por numero de página).
- Glosario/contexto refinado a modo `md-first` con filtro de ruido y preguntas de glosario en `choice` con opciones.
- Contexto jerarquico por nodos (`book`, ancestros y global) con escalado a niveles superiores bajo confirmacion por termino.
- Nuevo detector de descriptores conceptuales para incoherencias tipo `Lord Legislador` vs `rey malvado` y variantes de entorno tipo `cae ceniza` vs `cae nieve gris`.
- Nuevos detectores por página: overlap canónico, entidades faltantes/sobrantes, diferencias numericas, perdida de citas y desajuste por edad (`age.too_complex|age.too_childish`).
- Contrato enriquecido:
  - `pending_questions[]` con `reason` y `evidence_pages`.
  - `NN.issues.json` con `review_mode`, `canon_source`, `metrics`, `source/detector/confidence`.
  - `adaptation_context.json` con `analysis_policy`, `canon_sources` y glosario extendido (`variants`, `source_presence`, `evidence_pages`).
- Documentacion operativa alineada en `AGENTS.md`, `README.md`, `app/README.md`.
- Tarea: `docs/tasks/TAREA-020-contraste-canonico-obligatorio-pdf.md`.

## [16/02/26] - UI biblioteca Bulma + HTMX y rutas REST por página

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

- Eliminados módulos legacy/no usados de `app/` (migracion, stubs retirados y plantilla sin ruta activa).
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
