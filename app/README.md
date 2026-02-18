# App Flask de biblioteca

## Alcance de `app/`

- `app/` contiene solo la webapp Flask para navegar y editar el contrato final en `library/`.
- `app/` no ejecuta pipeline editorial ni usa CLI de ingesta.

## Contrato de datos consumido por la app

### Cuento (`NN.json`)

- top-level obligatorio:
  - `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
- `pages[]`:
  - `page_number`, `text`, `images.main` obligatorio, `images.secondary` opcional.
- slot (`cover`, `images.*`):
  - `status`, `prompt`, `active_id`, `alternatives[]`, `reference_ids[]` opcional.
- alternativa:
  - `id` (filename), `slug`, `asset_rel_path`, `mime_type`, `status`, `created_at`, `notes`.

### Meta por nodo (`meta.json`)

- rutas:
  - `library/meta.json` (global),
  - `library/<node>/meta.json`.
- minimos:
  - `collection.title`, `anchors[]`, `updated_at`.
- anchor mínimo:
  - `id`, `name`, `prompt`, `image_filenames[]`.
- ampliado para edición:
  - `status`, `active_id`, `alternatives[]`.

### Imágenes por nodo

- carpeta: `library/<node>/images/`
- assets: `<uuid>_<slug>.<ext>`
- índice: `library/<node>/images/index.json`

## Runtime web

- Sin SQLite.
- Catalogo por escaneo directo de `library/`.
- UI server-rendered con Jinja + Bulma y comportamiento parcial con HTMX.
- Endpoints principales:
  - `/`
  - `/<path_rel>` (nodo o cuento)
  - `/<book>/<NN>?p=N` (lectura por página)
  - `/<book>/<NN>?p=N&editor=1` (editor de página)
  - `/<book>/<NN>?editor=1` (editor de portada)
  - `/<story_path>/_fr/*` (fragmentos HTMX)
  - `/<story_path>/_act/*` (acciones editoriales)
  - `/media/<path>`
  - `/health`
- Rutas legacy removidas sin redirect:
  - `/browse/*`, `/story/*`, `/editor/story/*`, `/n/*`.

## Estructura UI

- `templates/layouts/`: shell principal.
- `templates/components/`: piezas reutilizables (tarjetas, breadcrumbs, slots).
- `templates/browse/`: vistas de biblioteca.
- `templates/story/read/`: lectura y panel avanzado.
- `templates/story/editor/`: edición de página, portada y anclas.
- `web/`: rutas por dominio (`browse` catch-all canónico, `story_editor` acciones, `fragments`, `system`).

## CLI de app

- `python manage.py runserver`
