# Cuentos Cosmere (App)

## Contrato de datos

- La biblioteca es canónica (`biblioteca/`).
- Cada cuento se identifica por carpeta con `meta.md` y páginas `NNN.md`.
- Cada página define texto y slots de imagen en frontmatter.
- El modelo relacional legacy queda solo para transición.

## Caché temporal

- Archivo objetivo: `db/library_cache.sqlite`.
- Uso: índice de navegación y lectura rápida.
- Estado stale: se detecta por fingerprint global de `biblioteca/`.
- Si la caché está stale, se bloquea guardado de imágenes hasta refrescar.

## CLI

- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py rebuild-cache`

Alias legacy:

- `python manage.py import` (deprecado)

## UI

- Navegación por árbol genérico de nodos.
- Vista de cuento por página (`/story/<path>?p=N`).
- Texto y prompts en modo lectura/copia.
- Subida o pegado de imagen por slot.
