# App del Generador de cuentos ilustrados

## Contrato de datos

- `library/` es la fuente de verdad.
- Un libro se detecta por uno o más archivos `NN.md`.
- Cada `NN.md` representa un cuento e incluye:
  - `## Meta`
  - `## Página NN`
  - `### Texto`
  - `### Prompts`
  - slots `#### <slot>` y `##### Requisitos` (YAML `tipo/ref`)
- La base SQLite es caché temporal, no verdad de negocio.

## Caché temporal

- Archivo: `db/library_cache.sqlite`.
- Uso: índice de navegación y lectura rápida.
- Estado stale: fingerprint global de `library/`.
- Escritura de imágenes bloqueada cuando la caché está stale.

## Comandos

- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py rebuild-cache`
- `python manage.py inbox-parse --input <path> --book <book_rel_path> --story-id <NN>`
- `python manage.py inbox-apply --batch-id <id> --approve`
- `python manage.py runserver`

## UI

- Navegación por árbol genérico de nodos.
- Detección de libro por presencia de `NN.md`.
- Vista de cuento por página (`/story/<path>?p=N`).
- Texto y prompts en modo lectura/copia.
- Subida o pegado de imagen por slot.
