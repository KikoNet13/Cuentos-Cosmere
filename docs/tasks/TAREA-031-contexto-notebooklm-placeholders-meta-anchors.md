# TAREA-031 - Contexto NotebookLM en placeholders + meta anchors

- Fecha: 18/02/26 22:08
- Estado: cerrada
- Versión objetivo: 2.7.1

## Resumen

Se corrigen los placeholders `NN_prompts.json` para que funcionen en NotebookLM sin depender de rutas/ficheros/webapp y se agrega el placeholder faltante para generar `meta.json` con anchors.

## Alcance implementado

1. Placeholders de cuentos actualizados (`01..11`):
   - bloque nuevo `CONTEXTO DISPONIBLE EN NOTEBOOKLM (IMPORTANTE)`;
   - elimina dependencia de rutas locales y webapp;
   - mantiene salida estricta en JSON puro (sin markdown, sin texto extra).
2. Reglas de referencias ajustadas para NB:
   - uso de anchors del `meta.json` (`style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`) en vez de lectura por rutas del repo.
3. Placeholder nuevo para meta/anchors:
   - `library/_inbox/Los juegos del hambre/meta_prompts.json`.
   - pide generar `meta.json` completo con `collection`, `anchors`, `style_rules`, `continuity_rules`, `updated_at`.

## Validaciones ejecutadas

1. Verificacion de estructura de placeholders:
   - 11 archivos de cuentos con patron `^\d{2}_prompts\.json$`.
2. Verificacion de contenido obligatorio:
   - presencia de `Devuelve SOLO JSON valido`;
   - presencia de `Sin markdown, sin explicaciones`;
   - presencia de bloque de contexto NotebookLM;
   - prohibicion explicita de depender de rutas/webapp.
3. Verificacion de meta placeholder:
   - `meta_prompts.json` existente;
   - instruccion de salida exacta para `meta.json`.
4. Resultado de validacion automática:
   - `PROMPT_PLACEHOLDERS_OK`.

## Notas operativas

1. No se restauraron backups.
2. No se modificaron `library/los_juegos_del_hambre/01..11.json`.
3. Este ajuste solo afecta la capa de orquestacion (placeholders para NB).

## Archivos principales tocados

- `library/_inbox/Los juegos del hambre/01_prompts.json`
- `library/_inbox/Los juegos del hambre/02_prompts.json`
- `library/_inbox/Los juegos del hambre/03_prompts.json`
- `library/_inbox/Los juegos del hambre/04_prompts.json`
- `library/_inbox/Los juegos del hambre/05_prompts.json`
- `library/_inbox/Los juegos del hambre/06_prompts.json`
- `library/_inbox/Los juegos del hambre/07_prompts.json`
- `library/_inbox/Los juegos del hambre/08_prompts.json`
- `library/_inbox/Los juegos del hambre/09_prompts.json`
- `library/_inbox/Los juegos del hambre/10_prompts.json`
- `library/_inbox/Los juegos del hambre/11_prompts.json`
- `library/_inbox/Los juegos del hambre/meta_prompts.json`
- `docs/tasks/TAREA-031-contexto-notebooklm-placeholders-meta-anchors.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
