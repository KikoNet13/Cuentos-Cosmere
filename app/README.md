# App del Generador de cuentos ilustrados

## Contrato de datos

- `library/` es la fuente de verdad.
- Un libro se detecta por uno o mas archivos `NN.json`.
- Cada `NN.json` representa un cuento completo con:
  - metadata de cuento
  - paginas (`text.original`, `text.current`)
  - slots de imagen (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen por slot + `active_id`
- Los assets de imagen viven en el mismo directorio del libro con nombre opaco `img_<uuid>_<slug>.<ext>`.

## Runtime

- Sin SQLite de cache.
- Catalogo por escaneo directo de `library/`.
- Endpoints de navegacion:
  - `/`
  - `/n/<path>`
  - `/story/<path>?p=N`
  - `/media/<path>`
  - `/health`

## Operaciones web

- Visualizar comparativa `original/current` de texto y prompts.
- Guardar edicion por pagina (`current`).
- Subir alternativas de imagen por slot.
- Marcar alternativa activa por slot.

## CLI

- `python manage.py runserver`

## Skill operativa

- Skill canonica: `revision-adaptacion-editorial`.
- El flujo de ingesta/editorial no usa comandos CLI dedicados.
