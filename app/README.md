# App del Generador de cuentos ilustrados

## Contrato de datos

- `library/` es la fuente de verdad.
- Un libro se detecta por uno o más archivos `NN.json`.
- Cada `NN.json` representa un cuento completo con:
  - metadatos de cuento
  - páginas (`text.original`, `text.current`)
  - slots de imagen (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen por slot y `active_id`
- Los assets de imagen viven en el mismo directorio del libro con nombre opaco `img_<uuid>_<slug>.<ext>`.

## Runtime

- Sin SQLite de caché.
- Catálogo por escaneo directo de `library/`.
- Endpoints principales:
  - `/`
  - `/n/<path>`
  - `/story/<path>?p=N` (modo lectura por defecto)
  - `/story/<path>?p=N&editor=1` (modo editorial)
  - `/media/<path>`
  - `/health`

## Operaciones web

- En lectura: render limpio de `text.current` + imagen activa.
- En editorial: comparativa `original/current`, guardado por página, gestión de alternativas por slot.
- Activación editorial solo por query `editor=1`.

## Pipeline editorial

- Entrada pública en código: `app/editorial_orquestador.py`.
- Función principal: `run_orquestador_editorial(...)`.
- Ciclo por severidad en cada etapa:
  - `critical -> major -> minor -> info`
- Ciclo interno por severidad:
  - detección
  - decisión interactiva
  - contraste con canon
- Etapas:
  - `text` primero
  - `prompt` después, solo si texto converge en `critical|major`

## Sidecars

`library/<book_rel_path>/_reviews/`:

- `context_chain.json`
- `glossary_merged.json`
- `pipeline_state.json`
- `NN.findings.json`
- `NN.choices.json`
- `NN.contrast.json`
- `NN.passes.json`

## CLI

- `python manage.py runserver`
