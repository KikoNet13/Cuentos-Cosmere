# Contratos de la skill adaptacion-ingesta-inicial

## Comando
```bash
python skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "<titulo>" [--book-rel-path "<ruta>"] [--answers-json "<archivo>"] [--dry-run]
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

## `pending_questions[]`
Campos usados:
- `id`: identificador estable (`book_rel_path`, `target_age`, `glossary::<slug>`).
- `kind`: `text` o `number`.
- `prompt`: pregunta para el usuario.
- `default`: valor sugerido (cuando aplica).
- `required`: boolean.
- `term`: termino ambiguo (solo glosario).

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
- `stories[]`
- `glossary[]` (`confirmed|pending`)
- `ambiguities[]`
- `notes[]`

## `NN.issues.json` (por cuento)
- `schema_version`
- `story_id`
- `story_rel_path`
- `generated_at`
- `summary` (`critical|major|minor|info`)
- `issues[]` con:
  - `issue_id`
  - `severity`
  - `category`
  - `page_number`
  - `evidence`
  - `suggested_action`
  - `status`
