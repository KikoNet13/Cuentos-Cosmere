# TAREA-037 - Copia de `meta_prompts` y exclusion de carpetas `_` en flujo de imagen

- Fecha: 19/02/26 01:00
- Estado: cerrada
- Version objetivo: 2.7.7

## Resumen

Se aplican dos ajustes solicitados para `Los juegos del hambre`:

1. Se copian los prompts de `meta_prompts.json` al `meta.json` activo del libro.
2. Se corrige el flujo `/_flow/image` para ignorar rutas con carpetas cuyo nombre empieza por `_`.

## Alcance aplicado

1. Meta de saga:
   - origen: `library/_inbox/Los juegos del hambre/meta_prompts.json`
   - destino: `library/los_juegos_del_hambre/meta.json`
2. Flujo guiado:
   - archivo: `app/web/image_flow.py`
   - funcion: `_is_in_excluded_area(...)`
   - regla nueva: excluir cualquier segmento de ruta que empiece por `_`.

## Validaciones ejecutadas

1. Copia de meta:
   - `META_MATCH=True` entre `meta_prompts.json` y `library/los_juegos_del_hambre/meta.json`.
   - `ANCHORS=27`.
2. Flujo de pendientes:
   - snapshot generado sin contexto de request.
   - `BAD_UNDERSCORE_ITEMS=0` en cola pendiente.

## Archivos tocados

- `library/los_juegos_del_hambre/meta.json`
- `app/web/image_flow.py`
- `docs/tasks/TAREA-037-meta-prompts-y-flow-exclusion-underscore.md`
