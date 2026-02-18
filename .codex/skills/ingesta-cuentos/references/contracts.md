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

- `NN.json` (preferido, 2 digitos).
- Partes permitidas:
  - `NN_a.json`, `NN_b.json`
  - `NN_a1.json`, `NN_a2.json`, `NN_b1.json`, `NN_b2.json`
- `meta.json` (opcional, por libro de inbox).
- `.md/.pdf` (ignorar + warning no bloqueante).

## Politica de lote

1. Resolucion por cuento:
   - priorizar `NN.json` valido;
   - si no existe, fusionar partes en memoria.
2. Si un cuento resuelto falla contrato, no se importa ningun cuento del lote.
3. Si parte esperada falta o no parsea, bloquear con error accionable.
4. Si hay colision con `library/<book_rel_path>/NN.json`, preguntar confirmacion por cuento.
5. Solo tras lote valido:
   - forzar `status=definitive`;
   - normalizar timestamps;
   - guardar en destino final.
6. Archivado post-import:
   - si el lote se completa sin pendientes, mover carpeta origen a `library/_processed/<book_title>/<timestamp>/`.

## Resolucion y fusion de partes

Combinaciones validas por cuento (`NN`):

1. `a + b`
2. `a1 + a2 + b`
3. `a + b1 + b2`
4. `a1 + a2 + b1 + b2`

Rangos esperados:

- `a`: paginas `1..8`
- `b`: paginas `9..16`
- `a1`: paginas `1..4`
- `a2`: paginas `5..8`
- `b1`: paginas `9..12`
- `b2`: paginas `13..16`

Reglas:

1. Cada parte debe parsear como JSON de cuento con top-level completo.
2. `pages[].page_number` debe caer en el rango del sufijo.
3. La union no puede tener duplicados de `page_number`.
4. La secuencia final debe ser `1..N` sin huecos.
5. Cover final:
   - preferir `a`,
   - si no existe, preferir `a1`,
   - si no, primer bloque valido.
6. Cover discrepante entre partes: warning no bloqueante.

## Contrato `NN.json` (canonico final)

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
- `reference_ids` (array opcional de strings)
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
- `input.pending_notebooklm`
- `input.missing_story_parts`
- `merge.invalid_part_range`
- `merge.duplicate_page_number`

## Warnings no bloqueantes recomendados

- `input.legacy_file_ignored`
- `input.meta_missing`
- `meta.optional_field_missing`
- `merge.cover_mismatch`

## Mensajes accionables para NotebookLM

Formato recomendado por error:

```text
[NN=<ID>] <codigo_error>
- Problema: <descripcion corta>
- Corrige asi: <instruccion concreta>
- Vuelve a entregar: <archivo exacto>
```

Fallback recomendado cuando se corta una parte:

```text
[NN=<ID>] input.pending_notebooklm
- Problema: el bloque <NN_a|NN_b> no llego como JSON completo.
- Corrige asi: reentrega en 4+4 con <NN_a1, NN_a2, NN_b1, NN_b2>.
- Vuelve a entregar: solo los archivos faltantes.
```
