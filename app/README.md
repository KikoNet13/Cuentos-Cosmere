# App del Generador de cuentos ilustrados

## Contrato de datos

- `library/` es la fuente de verdad.
- Un libro se detecta por uno o mas archivos `NN.md`.
- Cada `NN.md` representa un cuento e incluye:
  - `## Meta`
  - `## Pagina NN`
  - `### Texto`
  - `### Prompts`
  - slots `#### <slot>` y `##### Requisitos` (YAML `tipo/ref`)
- El glosario semantico puede declararse en `meta.md` por nodo con seccion `## Glosario` (tabla `termino|canonico|permitidas|prohibidas|notas`).
- El merge del glosario es jerarquico (`library/` -> nodo libro) y el nodo mas especifico pisa terminos repetidos.
- La base SQLite es cache temporal, no verdad de negocio.

## Cache temporal

- Archivo: `db/library_cache.sqlite`.
- Uso: indice de navegacion y lectura rapida.
- Estado stale: fingerprint global de `library/`.
- Escritura de imagenes bloqueada cuando la cache esta stale.

## Comandos

- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py rebuild-cache`
- `python manage.py inbox-parse --input <path> --book <book_rel_path> --story-id <NN>`
- `python manage.py inbox-review-validate --batch-id <id>`
- `python manage.py inbox-apply --batch-id <id> --approve`
- `python manage.py inbox-apply --batch-id <id> --approve --force --force-reason "<motivo>"`
- `python manage.py runserver`

## Carpetas de ingestion

- Entrada pendiente manual: `library/_pending/` (tus `.md` sin procesar).
- Salida parser/revision: `library/_inbox/<batch_id>/`.
- Artefactos IA por batch: `ai_context.json`, `review_ai.md`, `review_ai.json`.

## Gate IA en apply

- `inbox-apply` bloquea si falta `review_ai.json`, si es invalido, si `status` es `pending|blocked` o si `critical_open > 0`.
- `--force` exige `--force-reason` y deja trazabilidad en `manifest.json`.

## UI

- Navegacion por arbol generico de nodos.
- Deteccion de libro por presencia de `NN.md`.
- Vista de cuento por pagina (`/story/<path>?p=N`).
- Texto y prompts en modo lectura/copia.
- Subida o pegado de imagen por slot.
