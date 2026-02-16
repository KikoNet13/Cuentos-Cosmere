# App Flask de biblioteca

## Alcance de `app/`

- `app/` solo contiene la webapp Flask para navegación y edición puntual de cuentos en `library/`.
- `app/` no contiene ni ejecuta pipeline editorial de adaptación.
- Toda lógica de adaptación propuesta -> definitiva vive en skills `adaptacion-*`.

## Contrato de datos

- Fuente de verdad: `library/`.
- Un libro se detecta por uno o más archivos `NN.json`.
- Cada `NN.json` representa un cuento completo con:
  - metadatos de cuento
  - páginas (`text.original`, `text.current`)
  - slots de imagen (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen por slot y `active_id`
- Los assets de imagen viven en el mismo directorio del libro con nombre opaco `img_<uuid>_<slug>.<ext>`.

## Runtime web

- Sin SQLite de caché.
- Catálogo por escaneo directo de `library/`.
- Endpoints principales:
  - `/`
  - `/n/<path>`
  - `/story/<path>?p=N` (lectura)
  - `/story/<path>?p=N&editor=1` (edición puntual)
  - `/media/<path>`
  - `/health`

## Sidecars editoriales consumidos

- La app puede mostrar estado derivado de:
  - `library/<book>/_reviews/NN.review.json`
  - `library/<book>/_reviews/NN.decisions.log.jsonl`

## CLI de app

- `python manage.py runserver`

