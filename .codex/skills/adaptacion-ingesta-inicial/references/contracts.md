# Contratos de la skill adaptacion-ingesta-inicial

## Comando
```bash
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "<titulo>" [--book-rel-path "<ruta>"] [--answers-json "<archivo>"] [--dry-run]
```

## Envelope de salida
```json
{
  "phase": "awaiting_user|completed|failed",
  "pending_questions": [],
  "planned_outputs": [],
  "written_outputs": [],
  "metrics": {},
  "errors": []
}
```

## Semantica de `phase`
- `failed`: gate PDF bloqueante no superado o error de entrada.
- `awaiting_user`: preflight PDF correcto, faltan decisiones de usuario.
- `completed`: preflight PDF correcto y respuestas completas.

Si cualquier cuento del lote falla preflight PDF, el lote completo devuelve `failed` y no escribe salidas.

## `errors[]` (failed)
Errores estructurados con:
- `code`: `input.missing_pdf|pdf.parser_unavailable|pdf.unreadable|pdf.page_unreadable|...`
- `story_id` (cuando aplica)
- `message`
- `page_number` (solo para `pdf.page_unreadable`)

## `pending_questions[]`
Campos usados:
- `id`: identificador estable (`book_rel_path`, `target_age`, `glossary::<slug>`).
- `kind`: `text` o `number`.
- `prompt`: pregunta para el usuario.
- `default`: valor sugerido (cuando aplica).
- `required`: boolean.
- `term`: termino ambiguo (solo glosario).
- `reason`: `variant_conflict|pdf_only_term|md_only_term|entity_term` (solo glosario).
- `evidence_pages`: paginas donde aparece el termino (solo glosario).

## `answers-json`
Formato recomendado:
```json
{
  "answers": {
    "book_rel_path": "cosmere/nacidos-de-la-bruma-era-1/el-imperio-final",
    "target_age": 8,
    "glossary": {
      "Nacida de la bruma": "Nacida de la bruma",
      "atium": "atium"
    }
  }
}
```

Tambien se aceptan claves top-level (`book_rel_path`, `target_age`, `glossary`) sin wrapper `answers`.

## Contrato de salida de archivos

## `NN.json` (top-level extra)
- `story_title`
- `cover`
- `source_refs`
- `ingest_meta`

## `adaptation_context.json` (por libro)
- `schema_version`
- `book_rel_path`
- `book_title`
- `target_age`
- `updated_at`
- `analysis_policy`
- `canon_sources[]`
- `stories[]`
- `glossary[]`:
  - `term`
  - `status` (`confirmed|pending`)
  - `canonical`
  - `variants[]`
  - `source_presence` (`pdf|md|both`)
  - `evidence_pages[]`
- `ambiguities[]`
- `notes[]`

## `NN.issues.json` (por cuento)
- `schema_version`
- `story_id`
- `story_rel_path`
- `generated_at`
- `review_mode`
- `canon_source`
- `summary` (`critical|major|minor|info`)
- `metrics`
- `issues[]` con:
  - `issue_id`
  - `severity`
  - `category`
  - `page_number`
  - `evidence`
  - `suggested_action`
  - `status`
  - `source` (opcional):
    - `md_page_number`
    - `pdf_page_number`
    - `md_excerpt`
    - `pdf_excerpt`
  - `detector` (opcional)
  - `confidence` (opcional, `0.0..1.0`)

## Taxonomia de categorias principales
- Entrada/PDF:
  - `input.missing_pdf`
  - `pdf.parser_unavailable`
  - `pdf.unreadable`
  - `pdf.page_unreadable`
  - `pdf.page_count_mismatch`
- Canon:
  - `canon.low_page_overlap`
  - `canon.missing_entity`
  - `canon.extra_entity`
  - `canon.numeric_mismatch`
  - `canon.term_variant_noncanonical`
  - `canon.quote_loss`
- Edad:
  - `age.too_complex`
  - `age.too_childish`

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
