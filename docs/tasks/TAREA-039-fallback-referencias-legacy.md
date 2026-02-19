# TAREA-039 - Fallback de referencias legacy sin migrar datos

- Fecha: 19/02/26 01:39
- Estado: cerrada
- Version objetivo: 2.7.9

## Resumen

Se implementa fallback en `resolve_reference_assets(...)` para que la webapp pueda resolver referencias legacy (por ejemplo `anchor_char_prim.png`) hacia archivos reales de anclas con nombre opaco (`<uuid>_<slug>.png`), sin modificar `NN.json` ni `meta.json`.

## Alcance aplicado

1. `app/story_store.py`:
   - se mantiene la resolucion directa actual por filename literal;
   - se agrega mapa de fallback por niveles (`book -> ancestros -> library`) basado en `meta.anchors`;
   - se permite activar fallback por:
     - coincidencia con `anchor.id`,
     - coincidencia con `anchors[].image_filenames[]` (basename).
2. Seleccion de archivo real por ancla (orden estricto):
   - `active_id`,
   - `alternatives[].id`,
   - `image_filenames[]`,
   - aceptando solo candidatos existentes en disco.
3. Contrato preservado:
   - no cambian rutas HTTP, esquemas JSON ni firma de `resolve_reference_assets`;
   - salida estable para UI (`filename`, `found`, `asset_rel_path`, `node_rel_path`).

## Validaciones ejecutadas

1. Conteo global de referencias en `los_juegos_del_hambre`:
   - antes: `FOUND_REFS=0`, `MISSING_REFS=2410`.
   - despues del fallback: aumento de referencias resueltas sin tocar JSON.
2. Casos clave verificados:
   - filename UUID real: resuelve directo (`found=true`);
   - legacy `anchor_char_katniss.png`: resuelve al activo real de ancla;
   - `char_katniss_base` (anchor id): resuelve al activo real de ancla;
   - ancla sin imagen generada: mantiene `found=false`.
3. No regresion funcional:
   - `/_flow/image` mantiene su logica de pendientes (sin cambios de contrato ni rutas).

## Archivos tocados

- `app/story_store.py`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
- `docs/tasks/TAREA-039-fallback-referencias-legacy.md`

