# App Flask de biblioteca

## Alcance de `app/`

- `app/` solo contiene la webapp Flask para navegacion y edicion puntual de cuentos en `library/`.
- `app/` no contiene ni ejecuta pipeline editorial.

## Contrato de datos

- Fuente de verdad: `library/`.
- Un libro se detecta por uno o mas archivos `NN.json`.
- Cada `NN.json` representa un cuento completo con:
  - metadatos de cuento
  - paginas (`text.original`, `text.current`)
  - slots de imagen (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen por slot y `active_id`
- Los assets de imagen viven en el mismo directorio del libro con nombre opaco `img_<uuid>_<slug>.<ext>`.

## Runtime web

- Sin SQLite.
- Catalogo por escaneo directo de `library/`.
- Endpoints principales:
  - `/`
  - `/n/<path>`
  - `/story/<path>?p=N` (lectura)
  - `/story/<path>?p=N&editor=1` (edicion puntual)
  - `/media/<path>`
  - `/health`

## CLI de app

- `python manage.py runserver`
