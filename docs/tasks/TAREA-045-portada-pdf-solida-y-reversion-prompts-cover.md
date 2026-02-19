# TAREA-045 - Portada PDF con banda solida + reversion de prompts de cover

- Fecha: 19/02/26 22:22
- Estado: cerrada
- Responsable: Codex
- ADR relacionadas: `0008`

## Resumen
Se ajusta el exportador PDF para una portada mas editorial con banda superior solida y tipografia en blanco, y se revierten los prompts de portada `01..11` al formato anterior de maquetacion (sin texto exacto incrustado en prompt).

## Cambios aplicados
1. `app/pdf_export.py`
- Portada redisenada:
  - banda superior solida (sin transparencia),
  - titulo en blanco,
  - etiqueta de coleccion con numero en blanco (`LOS JUEGOS DEL HAMBRE · 01`).
- Tipografia refinada para todo el PDF:
  - prioridad de fuentes: `Garamond` -> `Palatino` -> `Georgia` -> `Cambria` -> `Times`.
- Se mantiene la regla de paginado narrativo:
  - pagina de texto con numeracion discreta,
  - pagina de imagen completa sin numero visible.

2. `library/los_juegos_del_hambre/01..11.json`
- Reversion del bloque de cover prompt al formato previo:
  - `MAQUETACION DE PORTADA (OBLIGATORIO)`
  - `GUIA DE MAQUETACION (ANCLAS)`
- Se retira el bloque nuevo que forzaba texto exacto arriba/abajo dentro del prompt.
- Se conservan referencias de maquetacion en portada:
  - `anchors/cover-title-format.png`
  - `anchors/cover-footer-collection-tag.png`.

3. Exportacion de validacion
- Se reactiva portada existente de `01` para poder exportar PDF final de control.
- Se genera `library/los_juegos_del_hambre/01.pdf` con la portada nueva.

## Validaciones ejecutadas
1. Compilacion
- `pipenv run python -m compileall app/pdf_export.py`

2. Validacion previa de export
- `pipenv run python manage.py export-story-pdf --story los_juegos_del_hambre/01 --dry-run`
- Resultado: `validation: OK`.

3. Export real
- `pipenv run python manage.py export-story-pdf --story los_juegos_del_hambre/01 --output library/los_juegos_del_hambre/01.pdf --overwrite`
- Resultado:
  - `layout_mode: paged`
  - `page_count: 33`
  - `spread_count: 33`

4. QA visual (render)
- `pipenv run python scripts/render_pdf_pages.py --input library/los_juegos_del_hambre/01.pdf --output-dir tmp/pdfs/01-cover-redesign-preview --dpi 160 --max-pages 4`
- Verificado:
  - portada con banda superior solida,
  - texto en blanco y numero de coleccion visible,
  - pagina de imagen sin numero visible.

## Archivos modificados
- `app/pdf_export.py`
- `library/los_juegos_del_hambre/meta.json`
- `library/los_juegos_del_hambre/01.json`
- `library/los_juegos_del_hambre/02.json`
- `library/los_juegos_del_hambre/03.json`
- `library/los_juegos_del_hambre/04.json`
- `library/los_juegos_del_hambre/05.json`
- `library/los_juegos_del_hambre/06.json`
- `library/los_juegos_del_hambre/07.json`
- `library/los_juegos_del_hambre/08.json`
- `library/los_juegos_del_hambre/09.json`
- `library/los_juegos_del_hambre/10.json`
- `library/los_juegos_del_hambre/11.json`
- `library/los_juegos_del_hambre/01.pdf`
- `library/los_juegos_del_hambre/images/index.json`
- `library/los_juegos_del_hambre/images/anchors/flow-cover-title-format.png`
- `library/los_juegos_del_hambre/images/anchors/flow-cover-footer-collection-tag.png`
- `docs/tasks/TAREA-045-portada-pdf-solida-y-reversion-prompts-cover.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`