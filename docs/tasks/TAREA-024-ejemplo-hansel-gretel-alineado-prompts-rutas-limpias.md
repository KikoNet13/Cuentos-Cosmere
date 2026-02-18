# TAREA-024 - Ejemplo Hansel/Gretel alineado + prompts de generación + rutas limpias

- Fecha: 18/02/26 10:05
- Estado: cerrada
- Versión objetivo: 2.1.0

## Resumen

Se alinea el ejemplo `library/hansel_y_gretel/01.json` con el nuevo set visual recortado sin texto incrustado, se reescriben prompts como prompts operativos largos para ChatGPT Image, se simulan anclas mediante `meta.json` + `reference_ids` (solo metadata), y se migra la webapp a rutas limpias sin prefijos legacy.

## Alcance implementado

1. Ejemplo Hansel/Gretel realineado:
   - reemplazo de assets activos (cover + páginas 1..15) usando `docs/assets/style_refs/Hansel y Gretel/`.
   - eliminacion de assets no usados del nodo.
   - regeneracion de `library/hansel_y_gretel/images/index.json` solo con activos.
2. Contrato del cuento:
   - `library/hansel_y_gretel/01.json` reescrito con:
     - texto narrativo en UTF-8 correcto,
     - prompts largos estructurados para cover y páginas 1..15,
     - `reference_ids` simulados por anclas,
     - página 16 con `images.main.status = not_required`, `active_id = \"\"`, `alternatives = []`.
   - espejo sincronizado en `library/hansel_y_gretel/hansel_y_gretel.json`.
3. Simulacion de anclas:
   - nuevo `library/hansel_y_gretel/meta.json` con `collection.title`, `anchors[]`, `updated_at`.
   - anclas de continuidad visual y de personajes/escenas con `image_filenames` simulados (sin archivos reales).
4. Migracion breaking de rutas:
   - ruta canónica única: `GET /<path_rel>`.
   - semantica de cuento:
     - `/<book>/<NN>`
     - `/<book>/<NN>?p=N`
     - `/<book>/<NN>?p=N&editor=1`
     - `/<book>/<NN>?editor=1` (editor de portada).
   - HTMX:
     - `GET /<story_path>/_fr/shell?p=N`
     - `GET /<story_path>/_fr/advanced?p=N`
     - `POST /<story_path>/_fr/slot/<slot_name>/activate?p=N`
   - acciones editoriales:
     - `POST /<story_path>/_act/page/save?p=N`
     - `POST /<story_path>/_act/page/slot/<slot_name>/upload?p=N`
     - `POST /<story_path>/_act/page/slot/<slot_name>/activate?p=N`
     - `POST /<story_path>/_act/cover/save|upload|activate`
     - `POST /<story_path>/_act/anchors/*`
   - rutas legacy eliminadas sin redirect:
     - `/browse/*`, `/story/*`, `/editor/story/*`, `/n/*`.
5. UI portada:
   - portada retirada de lectura por página (`story/read/_advanced_panel.html`).
   - portada retirada del editor por página (`story/editor/page.html`).
   - nuevo editor dedicado `story/editor/cover.html` accesible con `?editor=1` sin `p`.
6. Documentacion:
   - actualizados `AGENTS.md`, `README.md`, `app/README.md`.
   - actualizado `docs/tasks/INDICE.md` y `CHANGELOG.md`.

## Validaciones ejecutadas

1. `python -m compileall app`
   - resultado: compilacion correcta de `app/web/*`.
2. Smoke de rutas con `Flask test_client`:
   - `GET /`, `/hansel_y_gretel`, `/hansel_y_gretel/01`, `?p=7`, `?p=7&editor=1`, `?editor=1` -> `200`.
   - `GET /hansel_y_gretel/01/_fr/shell?p=7` -> `200`.
   - `GET /hansel_y_gretel/01/_fr/advanced?p=7` -> `200`.
   - `POST /hansel_y_gretel/01/_fr/slot/main/activate?p=7` -> `200`.
   - rutas legacy (`/browse/...`, `/story/...`, `/editor/story/...`, `/n/...`) -> `404`.
3. Validacion de datos de ejemplo (script local):
   - top-level obligatorio presente.
   - páginas secuenciales `1..16`.
   - páginas `1..15` con `active_id` válido y asset existente.
   - página `16` en `not_required` sin alternativa activa.
   - `images/index.json` coincide exactamente con activos usados.
   - `meta.json` cumple minimos (`collection.title`, `anchors[]`, `updated_at`).

## Archivos principales tocados

- `library/hansel_y_gretel/01.json`
- `library/hansel_y_gretel/hansel_y_gretel.json`
- `library/hansel_y_gretel/meta.json`
- `library/hansel_y_gretel/images/index.json`
- `library/hansel_y_gretel/images/*` (set activo recopiado)
- `app/web/common.py`
- `app/web/routes_browse.py`
- `app/web/routes_story_editor.py`
- `app/web/routes_fragments.py`
- `app/web/routes_story_read.py`
- `app/templates/components/breadcrumbs.html`
- `app/templates/components/story/page_nav.html`
- `app/templates/components/story/media_block.html`
- `app/templates/components/story/editor_slot_card.html`
- `app/templates/story/read/page.html`
- `app/templates/story/read/_shell.html`
- `app/templates/story/read/_advanced_panel.html`
- `app/templates/story/editor/page.html`
- `app/templates/story/editor/cover.html`
- `AGENTS.md`
- `README.md`
- `app/README.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
