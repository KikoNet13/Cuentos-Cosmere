# TAREA-043 - Maquetacion PDF en paginas cuadradas alternas

- Fecha: 19/02/26 14:38
- Estado: cerrada
- Responsable: Codex
- ADR relacionadas: `0008`

## Resumen
Se rediseña `export-story-pdf` para abandonar el layout en spreads `40x20` y pasar a paginas cuadradas `20x20` con secuencia fija:
1. Portada completa (imagen + titulo superpuesto).
2. Por cada pagina narrativa: una pagina de texto y luego una pagina de imagen.

Resultado esperado y validado en `01`: 33 paginas (`1 + 16 * 2`).

## Cambios aplicados
1. `app/pdf_export.py`:
- Nuevo layout `paged` por defecto en `export_story_pdf(...)`.
- Portada full-bleed con banda semitransparente superior y titulo centrado.
- Pagina narrativa dividida en dos:
  - pagina de texto dedicada (sin imagen),
  - pagina de imagen dedicada (`main` full-bleed).
- `secondary` no se maqueta en este modo, pero su validacion estructural se mantiene.
- Reflujo moderado de texto:
  - preserva saltos existentes,
  - introduce cortes de dialogo (`—`, `«`) de forma controlada,
  - divide parrafos largos por puntuacion,
  - mantiene linea en blanco entre parrafos.
- Tipografia editorial con fallback:
  - prioridad `Georgia` / `Georgia-Bold`,
  - fallback `Cambria` / `Cambria-Bold`,
  - fallback final portable `Times-Roman` / `Times-Bold`.
- Salida de `export_story_pdf(...)`:
  - agrega `layout_mode = "paged"`,
  - agrega `page_count`,
  - mantiene `spread_count` como alias de compatibilidad.

2. `manage.py`:
- `export-story-pdf` imprime `layout_mode` y `page_count` como datos principales.
- conserva `spread_count` si existe en el resultado.

3. `scripts/render_pdf_pages.py`:
- Nuevo script reproducible para renderizar PDF a PNG usando `pypdfium2`.
- Flags: `--input`, `--output-dir`, `--dpi`, `--max-pages`.

4. Dependencias:
- `Pipfile` y `Pipfile.lock` actualizados con `pypdfium2`.

## Validaciones ejecutadas
1. Compilacion:
- `pipenv run python -m compileall app/pdf_export.py manage.py scripts/render_pdf_pages.py`

2. Validacion estructural del cuento:
- `pipenv run python manage.py export-story-pdf --story los_juegos_del_hambre/01 --dry-run`
- Resultado: `validation: OK`.

3. Export real:
- `pipenv run python manage.py export-story-pdf --story los_juegos_del_hambre/01 --output tmp/pdfs/01-paged.pdf --overwrite`
- Resultado:
  - `layout_mode: paged`
  - `page_count: 33`
  - `spread_count: 33`

4. Render visual (skill PDF):
- `pipenv run python scripts/render_pdf_pages.py --input tmp/pdfs/01-paged.pdf --output-dir tmp/pdfs/01-preview --dpi 160 --max-pages 33`
- Resultado: `rendered_pages: 33` sin errores.

## QA visual (muestra revisada)
Se revisaron portada y paginas representativas de texto/imagen:
- `tmp/pdfs/01-preview/page-001.png` (portada),
- `tmp/pdfs/01-preview/page-002.png`, `tmp/pdfs/01-preview/page-004.png` (texto),
- `tmp/pdfs/01-preview/page-003.png` (imagen),
- `tmp/pdfs/01-preview/page-028.png`, `tmp/pdfs/01-preview/page-030.png` (texto con dialogos),
- `tmp/pdfs/01-preview/page-029.png`, `tmp/pdfs/01-preview/page-031.png` (imagen).

Conclusiones:
- portada legible con banda semitransparente,
- texto mas grande y respirable que en la version spread,
- dialogos mejor separados,
- alternancia texto/imagen consistente.

## Archivos modificados
- `app/pdf_export.py`
- `manage.py`
- `scripts/render_pdf_pages.py`
- `Pipfile`
- `Pipfile.lock`
- `docs/tasks/TAREA-043-maquetacion-pdf-paginas-cuadradas.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
