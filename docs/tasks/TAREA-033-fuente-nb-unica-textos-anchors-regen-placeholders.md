# TAREA-033 - Fuente NB única (.md) con textos y anchors + regen de placeholders

- Fecha: 18/02/26 22:16
- Estado: cerrada
- Versión objetivo: 2.7.3

## Resumen

Se pasa del enfoque de prompts largos inline a un enfoque de fuente única para NotebookLM:

1. Se genera un `.md` único con todos los textos de páginas y el listado canónico de anchors.
2. Se regeneran `01..11_prompts.json` para que apunten a esa fuente y no dependan de rutas/webapp.
3. Se actualiza `meta_prompts.json` para exigir inclusion de todos los anchors canónicos.

## Alcance implementado

1. Fuente nueva para NotebookLM:
   - `library/_inbox/Los juegos del hambre/FUENTE_NB_los_juegos_textos_y_anchors.md`
   - contenido:
     - sección de anchors canónicos (id, name, prompt, image_filenames),
     - sección de textos por cuento/pagina (`story_id`, `title`, `book_rel_path`, páginas 1..N).
2. Placeholders de cuentos regenerados (`01..11_prompts.json`):
   - instruyen revisar la fuente nueva;
   - mantienen salida JSON estricta sin texto adicional;
   - eliminan dependencia de rutas/ficheros locales;
   - fuerzan cobertura exacta de páginas por cuento.
3. `meta_prompts.json` regenerado:
   - exige `meta.json` completo;
   - exige incluir TODOS los anchors canónicos;
   - incluye listado explicito de IDs obligatorios.

## Validaciones ejecutadas

1. Verificacion de fuente nueva:
   - archivo `.md` generado y no vacio.
2. Verificacion de placeholders:
   - 11 archivos de cuentos detectados (`^\\d{2}_prompts\\.json$`);
   - todos referencian `FUENTE_NB_los_juegos_textos_y_anchors.md`;
   - todos mantienen reglas de salida estricta.
3. Verificacion de meta placeholder:
   - `meta_prompts.json` contiene regla de inclusion total de anchors + IDs obligatorios.
4. Resultado automatizado:
   - `NB_SOURCE_AND_PLACEHOLDERS_OK`.

## Notas operativas

1. No se restauraron backups.
2. No se modificaron `library/los_juegos_del_hambre/01..11.json`.
3. Este cambio afecta solo la capa de orquestacion a NotebookLM.

## Archivos principales tocados

- `library/_inbox/Los juegos del hambre/FUENTE_NB_los_juegos_textos_y_anchors.md`
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
- `docs/tasks/TAREA-033-fuente-nb-unica-textos-anchors-regen-placeholders.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
