# Esquema JSON v1

## Top-level

- `schema_version`
- `story_id`
- `title`
- `status`
- `book_rel_path`
- `created_at`
- `updated_at`
- `pages[]`

## Pagina

- `page_number`
- `status`
- `text.original`
- `text.current`
- `images.main`
- `images.secondary` (opcional)

## Slot de imagen

- `status`
- `prompt.original`
- `prompt.current`
- `active_id`
- `alternatives[]`

## Alternativa

- `id`
- `slug`
- `asset_rel_path`
- `mime_type`
- `status`
- `created_at`
- `notes`
