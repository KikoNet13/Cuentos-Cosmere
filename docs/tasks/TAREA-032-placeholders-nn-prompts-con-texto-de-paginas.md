# TAREA-032 - Placeholders `NN_prompts.json` con texto de paginas para NotebookLM

- Fecha: 18/02/26 22:11
- Estado: cerrada
- Version objetivo: 2.7.2

## Resumen

Se actualizan los placeholders de prompts por cuento para incluir el texto narrativo completo por pagina, de modo que NotebookLM pueda generar prompts sin depender de conocer previamente las paginas adaptadas.

## Alcance implementado

1. Placeholders de cuentos (`01..11`) actualizados:
   - se agrega bloque `TEXTO BASE DEL CUENTO (USAR COMO FUENTE NARRATIVA PARA PAGE_PROMPTS)`;
   - incluye `page_number` + `text` para todas las paginas del cuento;
   - instruccion explicita de no inventar/cambiar orden de paginas.
2. Se mantiene el contexto NB previamente incorporado:
   - fuentes canonicas,
   - ejemplo Hansel y Gretel,
   - fuente de estilo,
   - sin dependencia de rutas/webapp.
3. Se mantiene contrato de salida estricto:
   - solo JSON valido,
   - sin markdown ni texto extra,
   - salida exacta del `NN_prompts.json` objetivo.

## Validaciones ejecutadas

1. Verificacion de presencia del nuevo bloque de texto base:
   - 11 placeholders con seccion `TEXTO BASE DEL CUENTO...`.
2. Verificacion de estructura minima del bloque:
   - presencia de `"page_number":` y `"text":` en todos los archivos.
3. Resultado:
   - `PAGE_TEXT_SECTION_OK`.

## Notas operativas

1. No se restauraron backups.
2. No se modificaron `library/los_juegos_del_hambre/01..11.json`.
3. `meta_prompts.json` se conserva sin cambios en esta tarea.

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
- `docs/tasks/TAREA-032-placeholders-nn-prompts-con-texto-de-paginas.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
