# App del Generador de cuentos ilustrados

## Contrato de datos

- `library/` es la fuente de verdad.
- Un libro se detecta por uno o mas archivos `NN.json`.
- Cada `NN.json` representa un cuento completo con:
  - metadatos de cuento
  - paginas (`text.original`, `text.current`)
  - slots de imagen (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen por slot y `active_id`
- Los assets de imagen viven en el mismo directorio del libro con nombre opaco `img_<uuid>_<slug>.<ext>`.

## Runtime web

- Shell SPA (Flask + template minimo):
  - `/` -> redirige a `/biblioteca`
  - `/biblioteca`
  - `/biblioteca/<path>`
  - `/cuento/<path>`
- Media:
  - `/media/<path>`

## API v1

- `GET /api/v1/library/node`
- `GET /api/v1/stories/<path>`
- `PATCH /api/v1/stories/<path>/pages/<int:page_number>`
- `POST /api/v1/stories/<path>/pages/<int:page_number>/slots/<slot_name>/alternatives`
- `PUT /api/v1/stories/<path>/pages/<int:page_number>/slots/<slot_name>/active`
- `GET /api/v1/health`

Todas las respuestas usan envoltura uniforme:

```json
{
  "ok": true,
  "data": {},
  "error": null
}
```

## Frontend

- Codigo fuente: `frontend/`
- Build de Vite a `app/static/spa/` con assets fijos `app.js` y `app.css`.
- El directorio compilado se ignora en git.

## Tests

- `python -m unittest discover -s tests`

## CLI

- `python manage.py runserver`
