# App del Generador de cuentos ilustrados

## Contrato de datos

- `biblioteca/` es la fuente de verdad.
- Un cuento se identifica por carpeta con `meta.md` y páginas `NNN.md`.
- Cada página define su texto y slots de imagen en frontmatter.
- La base SQLite es caché temporal, no verdad de negocio.

## Caché temporal

- Archivo: `db/library_cache.sqlite`.
- Uso: índice de navegación y lectura rápida.
- Estado stale: fingerprint global de `biblioteca/`.
- Escritura de imágenes bloqueada cuando la caché está stale.

## Comandos

- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py rebuild-cache`
- `python manage.py runserver`

## UI

- Navegación por árbol genérico de nodos.
- Vista de cuento por página (`/story/<path>?p=N`).
- Texto y prompts en modo lectura/copia.
- Subida o pegado de imagen por slot.
