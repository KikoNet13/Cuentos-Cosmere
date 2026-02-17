# Contratos de la skill adaptacion-ingesta-inicial

## Interfaz publica

- Esta skill es conversacional.
- No existe comando CLI, ni envelope ejecutable (`phase`, `pending_questions`, etc.).
- El agente ejecuta el flujo completo en chat y escribe archivos en `library/`.

## Definicion de entradas

- Carpeta base: `library/_inbox/<inbox_book_title>/`
- Archivos de entrada por cuento:
  - `NN.md`: propuesta inicial del cuento.
  - `NN.pdf`: fuente oficial/canonica para contraste de fiabilidad.
- Descubrimiento:
  - procesar todos los `NN.md`;
  - excluir `_ignore/`;
  - pairing obligatorio `NN.md` + `NN.pdf`.

## Politica de bloqueo canonico

- Bloqueo inmediato por lote si cualquier cuento no se puede contrastar contra PDF canonico.
- Codigos base de bloqueo:
  - `input.missing_pdf`
  - `pdf.skill_unavailable`
  - `pdf.unreadable`
  - `pdf.insufficient_story_signal`
- Regla de paginas no textuales:
  - paginas aisladas de portada/mapa no bloquean si el conjunto del PDF aporta senal narrativa suficiente.

## Protocolo conversacional obligatorio

1. Preguntar `target_age` (obligatorio).
2. Preguntar/confirmar `book_rel_path` en slug canonico (obligatorio).
3. Glosario ambiguo:
   - preguntar todos los ambiguos detectados;
   - una pregunta por turno con opciones y una opcion recomendada;
   - excepcion: una sola pregunta para resolver una incoherencia repetida en multiples ocurrencias.
4. Escalado de contexto:
   - la skill propone el nivel;
   - el usuario confirma cuando impacta varios cuentos o nodos.

## Politica de analisis

- Canon manda: `NN.pdf`.
- Cobertura de terminos: `md-first expandido`.
  - candidatos parten de `NN.md`;
  - solo se agregan terminos del PDF cuando desbloquean una incoherencia real de `NN.md`.
- Deteccion de incoherencias:
  - enfoque generico, sin hardcode de ejemplos del usuario;
  - lista base de tipos obligatorios + tipos ampliables con justificacion.

## Contrato de salida de archivos

## `NN.json`

Archivo: `library/<book_rel_path>/NN.json`

Top-level minimo:
- `schema_version`
- `story_id`
- `title`
- `story_title`
- `status` (`in_review|definitive` y lectura no bloqueante de estados legacy)
- `book_rel_path`
- `created_at`
- `updated_at`
- `cover`
- `source_refs`
- `ingest_meta`
- `pages`

`cover`:
- `status` (`pending|draft|approved`)
- `prompt.original`
- `prompt.current`
- `asset_rel_path`
- `notes`

`source_refs`:
- `proposal_md_rel_path`
- `reference_pdf_rel_path`
- `inbox_book_title`

`ingest_meta`:
- `phase` (`initial_ingest`)
- `target_age`
- `generated_at`
- `generated_by` (`adaptacion-ingesta-inicial`)
- `semantic_mode` (`codex_chat`)

Pagina minima:
- `page_number`
- `status`
- `text.original`
- `text.current`
- `images.main`
- `images.secondary` (opcional)

## `adaptation_context.json`

Archivo: `library/<book_rel_path>/_reviews/adaptation_context.json`

Campos:
- `schema_version`
- `context_scope` (`book|ancestor|global`)
- `node_rel_path`
- `book_rel_path`
- `book_title`
- `target_age`
- `updated_at`
- `analysis_policy`
- `canon_sources`
- `stories`
- `glossary`
- `ambiguities`
- `notes`

`glossary[]`:
- `term`
- `status` (`confirmed|pending`)
- `canonical`
- `variants`
- `source_presence` (`pdf|md|both`)
- `evidence_pages`
- `scope` (`story|book|ancestor|global`)

## `NN.issues.json`

Archivo: `library/<book_rel_path>/_reviews/NN.issues.json`

Top-level:
- `schema_version`
- `story_id`
- `story_rel_path`
- `generated_at`
- `review_mode`
- `canon_source`
- `summary` (`critical|major|minor|info`)
- `metrics`
- `issues`

`issues[]`:
- `issue_id`
- `severity`
- `category`
- `page_number`
- `evidence`
- `suggested_action`
- `status` (`open|pending|confirmed|resolved`)
- `source` (opcional):
  - `md_page_number`
  - `pdf_page_number`
  - `md_excerpt`
  - `pdf_excerpt`
- `detector` (opcional)
- `confidence` (opcional, `0.0..1.0`)

## Tipos base de issue

Entrada/PDF:
- `input.missing_pdf`
- `pdf.skill_unavailable`
- `pdf.unreadable`
- `pdf.insufficient_story_signal`

Canon:
- `canon.low_page_overlap`
- `canon.missing_entity`
- `canon.extra_entity`
- `canon.numeric_mismatch`
- `canon.term_variant_noncanonical`
- `canon.descriptor_variant_noncanonical`
- `canon.quote_loss`

Edad:
- `age.too_complex`
- `age.too_childish`

Tipos nuevos:
- permitidos si se documenta justificacion en `detector` o `notes`.

## Umbrales de edad (modo equilibrado)

Deteccion por pagina sobre `text.original/current`:
- metricas:
  - `avg_sentence_length`
  - `long_word_ratio` (palabras >= 10 caracteres)
  - `exclamation_ratio`
  - `childish_marker_ratio`
- reglas:
  - `target_age <= 7`: complejo si `avg_sentence_length > 16` o `long_word_ratio > 0.17`.
  - `8 <= target_age <= 10`: complejo si `avg_sentence_length > 20` o `long_word_ratio > 0.20`; infantil si `childish_marker_ratio > 0.055` y `avg_sentence_length < 11`.
  - `target_age >= 11`: complejo si `avg_sentence_length > 24` o `long_word_ratio > 0.23`; infantil si `childish_marker_ratio > 0.035` y `avg_sentence_length < 12`, o `exclamation_ratio > 0.03`.

## Escritura incremental (modo conversacional)

- Durante el dialogo se escriben salidas parciales en archivos finales.
- `NN.json` debe mantenerse en `status: in_review` hasta cierre editorial.
- `adaptation_context.json` y `NN.issues.json` reflejan estados de trabajo (`pending|confirmed|open`) segun avance de respuestas.
- Al cierre de ronda se consolida `updated_at`, resumen de severidad y decisiones confirmadas.
