# Contratos - ingesta-cuentos

## Interfaz publica

- Skill conversacional en chat.
- Sin CLI ni scripts internos.
- Entrada desde `library/_inbox/`.
- Salida final en `library/`.
- Artefacto operativo adicional por saga:
  - `library/<book_rel_path>/chatgpt_project_setup.md`.

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

Codificacion de entrada:

- JSON en UTF-8 y UTF-8 BOM (ambos aceptados).

## Politica de lote

1. Resolucion por cuento:
   - priorizar `NN.json` válido;
   - si no existe, fusionar partes en memoria.
2. Si un cuento resuelto falla contrato, no se importa ningun cuento del lote.
3. Si parte esperada falta o no parsea, bloquear con error accionable.
4. Si hay colision con `library/<book_rel_path>/NN.json`, preguntar confirmacion por cuento.
5. Enriquecimiento preimport de refs (si hay `meta.json` válido):
   - respetar refs existentes;
   - autocompletar faltantes con anclas de `meta`;
   - reportar warnings de cobertura.
6. Solo tras lote válido:
   - forzar `status=definitive`;
   - normalizar timestamps;
   - guardar en destino final.
7. Archivado post-import:
   - si el lote se completa sin pendientes, mover carpeta origen a `library/_processed/<book_title>/<timestamp>/`.
8. Dossier por saga:
   - tras importacion válida, regenerar `chatgpt_project_setup.md`.
   - debe incluir setup de ChatGPT Project, checklist de anclas, flujo por slot y QA.
9. Refresh manual:
   - permitido regenerar `chatgpt_project_setup.md` para un libro ya importado sin reimportar `NN.json`.

## Resolucion y fusion de partes

Combinaciones válidas por cuento (`NN`):

1. `a + b`
2. `a1 + a2 + b`
3. `a + b1 + b2`
4. `a1 + a2 + b1 + b2`

Rangos esperados:

- `a`: páginas `1..8`
- `b`: páginas `9..16`
- `a1`: páginas `1..4`
- `a2`: páginas `5..8`
- `b1`: páginas `9..12`
- `b2`: páginas `13..16`

Reglas:

1. Cada parte debe parsear como JSON de cuento con top-level completo.
2. `pages[].page_number` debe caer en el rango del sufijo.
3. La union no puede tener duplicados de `page_number`.
4. La secuencia final debe ser `1..N` sin huecos.
5. Cover final:
   - preferir `a`,
   - si no existe, preferir `a1`,
   - si no, primer bloque válido.
6. Cover discrepante entre partes: warning no bloqueante.

## Contrato `NN.json` (canónico final)

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

## Convencion operativa de `reference_ids`

1. `reference_ids` debe apuntar a filenames declarados en `meta.anchors[].image_filenames[]`.
2. `reference_ids` no debe usar IDs opacos de alternativas (`<uuid>_<slug>.<ext>`) como convension principal.
3. Estrategia hibrida recomendada:
   - NotebookLM propone refs cuando puede.
   - `ingesta-cuentos` completa faltantes antes de importar.
4. Si un slot tiene `status = not_required`, se permite `reference_ids` vacio.

## Enriquecimiento automático de referencias

1. Precondicion:
   - existe `meta.json` válido del libro/lote.
2. Slots objetivo:
   - `cover`
   - `pages[].images.main`
3. Regla de precedencia:
   - preservar refs existentes;
   - completar faltantes con anchors `style_*` + anchors semanticos detectados por texto/prompt;
   - eliminar duplicados preservando orden.
4. Politica de validacion:
   - autocompletar + warning (no bloqueo) si hay `meta`.
   - si no hay `meta`, no bloquear por refs; reportar warning operativo.

## Contrato `meta.json` por nodo

Rutas válidas:

- `library/meta.json` (global)
- `library/<node>/meta.json`

Minimos:

- `collection.title`
- `anchors` (array)
- `updated_at`

Anchor mínimo:

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

Operativo recomendado para flujo listo de imagen:

- incluir categorias por prefijo: `style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`.

## Dossier operativo `chatgpt_project_setup.md`

Ruta:

- `library/<book_rel_path>/chatgpt_project_setup.md`

Naturaleza:

- artefacto operativo (no canónico del cuento);
- se regenera tras cada ingesta válida;
- puede refrescarse manualmente sin reimport.
- plantilla de referencia para contenido base:
  - `.codex/skills/ingesta-cuentos/references/chatgpt_project_setup_template.md`.

Contenido mínimo:

1. nombre sugerido del Project por saga.
2. instrucciones maestras de continuidad visual.
3. checklist de fase obligatoria de anclas antes de páginas.
4. flujo operativo por slot (portada/pagina) para ciclo rapido `copiar -> generar -> pegar`.
5. politica de QA rapido.
6. troubleshooting de portapapeles/navegador.

## índice de imágenes por nodo

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
- `refs.autofilled`
- `refs.style_only_fallback`
- `refs.anchor_missing`

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
