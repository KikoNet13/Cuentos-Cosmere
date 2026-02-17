# App Flask de biblioteca

## Alcance de `app/`

- `app/` solo contiene la webapp Flask para navegacion y edicion puntual de cuentos en `library/`.
- `app/` no contiene ni ejecuta pipeline editorial.

## Contrato de datos

- Fuente de verdad: `library/`.
- Un libro se detecta por uno o mas archivos `NN.json`.
- Cada `NN.json` representa un cuento completo con:
  - metadatos de cuento (`title`, `story_title`, `status`, etc.)
  - metadatos de ingesta inicial (`cover`, `source_refs`, `ingest_meta`)
  - paginas (`text.original`, `text.current`)
  - slots de imagen (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen por slot y `active_id`
- Los assets de imagen viven en el mismo directorio del libro con nombre opaco `img_<uuid>_<slug>.<ext>`.
- Estados aceptados de cuento: legacy (`draft`, `ready`, etc.) y flujo actual (`in_review`, `definitive`).
- La ingesta inicial externa (`.codex/skills/adaptacion-ingesta-inicial`) es conversacional, aplica gate PDF obligatorio por lote y escribe resultados en JSON; `app/` solo consume esos resultados.

## Runtime web

- Sin SQLite.
- Catalogo por escaneo directo de `library/`.
- UI server-rendered con Jinja + Bulma y comportamiento parcial con HTMX.
- Endpoints principales:
  - `/`
  - `/browse/<path>`
  - `/story/<path>/page/<int:page_number>` (lectura)
  - `/editor/story/<path>/page/<int:page_number>` (edicion puntual)
  - `/fragments/story/<path>/page/<int:page_number>/*` (fragmentos HTMX)
  - `/media/<path>`
  - `/health`
- Compatibilidad legacy con redirect:
  - `/n/<path>`
  - `/story/<path>?p=N[&editor=1]`

## Estructura UI

- `templates/layouts/`: shell principal.
- `templates/components/`: piezas reutilizables (tarjetas, breadcrumbs, navegacion).
- `templates/browse/`: vistas de biblioteca.
- `templates/story/read/`: lectura y fragmentos HTMX.
- `templates/story/editor/`: edicion por pagina.
- `web/`: rutas separadas por dominio (`browse`, `story_read`, `story_editor`, `fragments`, `system`).

## CLI de app

- `python manage.py runserver`
