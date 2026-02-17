# Contratos - ingesta-cuentos

## Interfaz publica

- Skill conversacional en chat.
- Sin CLI ni scripts internos.
- Entrada desde `library/_inbox/`.
- Salida final en `library/`.

## Entradas

Ruta de lote:

- `library/_inbox/<book_title>/`

Archivos:

- `NN.json` (obligatorio, 2 digitos).
- `meta.json` (opcional, por libro de inbox).
- `.md/.pdf` (ignorar + warning no bloqueante).

## Politica de lote

1. Si un `NN.json` falla contrato, no se importa ningun cuento del lote.
2. Si hay colision con `library/<book_rel_path>/NN.json`, preguntar confirmacion por cuento.
3. Solo tras lote valido:
   - forzar `status=definitive`;
   - normalizar timestamps;
   - mover a destino final.

## Contrato `NN.json` (nuevo, unico)

Top-level obligatorio:

- `story_id` (string)
- `title` (string)
- `status` (string)
- `book_rel_path` (string)
- `created_at` (string ISO)
- `updated_at` (string ISO)
- `cover` (slot)
- `pages` (array)

`pages[]`:

- `page_number` (int)
- `text` (string)
- `images.main` (slot obligatorio)
- `images.secondary` (slot opcional)

Secuencia:

- `page_number` debe ser `1..N` sin huecos.

Slot (`cover` / `images.*`):

- `status` (string)
- `prompt` (string)
- `reference_ids` (array opcional de filenames con extension)
- `active_id` (string)
- `alternatives` (array)

Alternativa:

- `id` (filename con extension)
- `slug` (string)
- `asset_rel_path` (string)
- `mime_type` (string)
- `status` (string)
- `created_at` (string ISO)
- `notes` (string)

## Contrato `meta.json` por nodo

Rutas validas:

- `library/meta.json` (global)
- `library/<node>/meta.json`

Minimos:

- `collection.title`
- `anchors` (array)
- `updated_at`

Anchor minimo:

- `id`
- `name`
- `prompt`
- `image_filenames[]`

Anchor ampliado permitido:

- `status`
- `active_id`
- `alternatives[]`

Opcionales globales:

- `style_rules`
- `continuity_rules`

## Indice de imagenes por nodo

Ruta:

- `library/<node>/images/index.json`

Entrada minima:

- `filename`
- `asset_rel_path`
- `description`
- `node_rel_path`
- `created_at`

## Normalizaciones de importacion

1. `story_id` se alinea al nombre de archivo `NN`.
2. `status` se fuerza a `definitive`.
3. `created_at` se autocompleta si falta.
4. `updated_at` se refresca siempre.
5. `book_rel_path` se reemplaza por el destino confirmado del lote.

## Errores bloqueantes recomendados

- `contract.invalid_json`
- `contract.missing_required_field`
- `contract.invalid_page_sequence`
- `contract.invalid_slot`
- `contract.invalid_alternative`
- `contract.empty_pages`

## Warnings no bloqueantes recomendados

- `input.legacy_file_ignored`
- `input.meta_missing`
- `meta.optional_field_missing`

## Mensajes accionables para NotebookLM

Formato recomendado por error:

```text
[NN=<ID>] <codigo_error>
- Problema: <descripcion corta>
- Corrige asi: <instruccion concreta>
- Vuelve a entregar: <archivo exacto>
```
