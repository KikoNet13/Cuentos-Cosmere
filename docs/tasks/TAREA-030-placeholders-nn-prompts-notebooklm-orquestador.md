# TAREA-030 - Placeholders `NN_prompts.json` para NotebookLM por cuento (orquestador)

- Fecha: 18/02/26 22:00
- Estado: cerrada
- Version objetivo: 2.7.0

## Resumen

Se implementa un parche de orquestacion para pedir a NotebookLM los prompts completos por cuento sin tocar ahora `NN.json`:

1. Se crean placeholders `NN_prompts.json` en texto plano, listos para copiar/pegar en NotebookLM.
2. Cada placeholder exige salida estricta en JSON valido y sin texto extra.
3. El resultado esperado de NB se vuelca en el mismo `NN_prompts.json` para preparar un merge posterior.

## Alcance implementado

1. Creada carpeta de lote:
   - `library/_inbox/Los juegos del hambre/`
2. Creados placeholders por cuento:
   - `01_prompts.json` ... `11_prompts.json`
3. Cada placeholder incluye prompt a NB con reglas estrictas:
   - `Devuelve SOLO JSON valido`
   - `Sin markdown, sin explicaciones`
   - `No incluyas nada fuera del JSON`
   - `Tu respuesta debe ser EXACTAMENTE el contenido final del archivo NN_prompts.json`
4. Schema exigido a NB en cada archivo:
   - `story_id`
   - `title`
   - `book_rel_path`
   - `updated_at`
   - `cover_prompt`
   - `page_prompts[]` (`page_number`, `main_prompt`)
   - `secondary_prompts[]` opcional (solo si aplica)
5. Reglas de calidad de prompts incluidas en el texto a NB:
   - cover: 8 bloques, 900-1700 chars
   - main: 8 bloques, 700-1500 chars
   - continuidad por personajes/entorno/props
   - uso de `reference_ids` del cuento fuente

## Validaciones ejecutadas

1. Estructura de archivos:
   - verificacion de 11 archivos con patron `^\d{2}_prompts\.json$`
2. Validacion de contenido placeholder:
   - cada archivo contiene las clausulas obligatorias de salida estricta.
3. Resultado:
   - `PLACEHOLDER_VALIDATION_OK`

## Notas operativas

1. No se restauraron backups.
2. No se modificaron `library/los_juegos_del_hambre/01..11.json` en esta tarea.
3. El merge desde `NN_prompts.json` a `NN.json` queda fuera de esta tarea.

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
- `docs/tasks/TAREA-030-placeholders-nn-prompts-notebooklm-orquestador.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
