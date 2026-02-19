# TAREA-044 - Ajuste fino de portada, espaciado y numeracion en PDF

- Fecha: 19/02/26 15:47
- Estado: cerrada
- Responsable: Codex
- ADR relacionadas: `0008`

## Resumen
Se refina `export-story-pdf` en layout `paged` sin tocar datos editoriales (`NN.json`):
1. Portada con tratamiento visual mas contrastado.
2. Etiqueta de coleccion en pie (`LOS JUEGOS DEL HAMBRE - CUENTO 01`).
3. Texto narrativo con espaciado mas compacto.
4. Numeracion visible de exportacion en paginas narrativas (`1..32`) y portada sin numero.

## Cambios aplicados
1. `app/pdf_export.py`:
- Portada:
  - se mantiene imagen `cover` full-bleed,
  - nuevo panel superior de alto contraste para titulo,
  - sombreado inferior,
  - etiqueta de coleccion en pie con formato automatico desde `book_rel_path` + `story_id`.
- Texto:
  - `_normalize_story_text(...)` corrige deteccion de dialogo con Unicode real (`\u2014`, `\u00AB`),
  - preserva saltos existentes sin insertar dobles separaciones artificiales,
  - elimina mojibake previo en las reglas de corte,
  - `_wrap_text(...)` deja de agregar linea en blanco por defecto entre todos los bloques,
  - `_fit_text_block(...)` usa interlineado mas compacto (`1.38x`).
- Numeracion:
  - se elimina cabecera tipo titulo `Pagina N`,
  - se agrega contador interno de exportacion (independiente de `pages[].page_number`),
  - se pinta numero discreto en pie para cada pagina narrativa (texto e imagen),
  - portada permanece sin numeracion visible.
- Contrato de salida preservado:
  - `layout_mode = "paged"`,
  - `page_count` canonico,
  - `spread_count` como alias compatible.

## Validaciones ejecutadas
1. Compilacion:
- `pipenv run python -m compileall app/pdf_export.py`

2. Validacion estructural:
- `pipenv run python manage.py export-story-pdf --story los_juegos_del_hambre/01 --dry-run`
- Resultado: `validation: OK`.

3. Export real:
- `pipenv run python manage.py export-story-pdf --story los_juegos_del_hambre/01 --output tmp/pdfs/01-paged-v2.pdf --overwrite`
- Resultado:
  - `layout_mode: paged`
  - `page_count: 33`
  - `spread_count: 33`

4. Render visual (skill PDF):
- `pipenv run python scripts/render_pdf_pages.py --input tmp/pdfs/01-paged-v2.pdf --output-dir tmp/pdfs/01-preview-v2 --dpi 160 --max-pages 33`
- Resultado: `rendered_pages: 33`.

## QA visual (muestra revisada)
Paginas inspeccionadas:
- `tmp/pdfs/01-preview-v2/page-001.png` (portada)
- `tmp/pdfs/01-preview-v2/page-002.png` (texto + numero 1)
- `tmp/pdfs/01-preview-v2/page-003.png` (imagen + numero 2)
- `tmp/pdfs/01-preview-v2/page-028.png` (texto dialogado + numero 27)
- `tmp/pdfs/01-preview-v2/page-029.png` (imagen + numero 28)
- `tmp/pdfs/01-preview-v2/page-033.png` (imagen final + numero 32)

Conclusiones:
- portada mas impactante y con etiqueta de coleccion profesional en pie,
- espaciado de texto mas compacto (sin saltos extra automaticos),
- numeracion de exportacion correcta y continua `1..32`,
- portada sin numero visible,
- sin cambios en `library/los_juegos_del_hambre/01.json`.

## Archivos modificados
- `app/pdf_export.py`
- `docs/tasks/TAREA-044-ajuste-fino-portada-espaciado-numeracion-pdf.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`