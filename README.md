# Generador de cuentos ilustrados

Proyecto local para revisar, adaptar y publicar cuentos ilustrados con fuente de verdad en JSON por cuento.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canonico: un cuento por archivo `NN.json` dentro de un nodo libro.
- Runtime sin SQLite: la app navega por escaneo directo de disco.
- Frontend actual: SPA `Vue + Vite` servida por Flask.
- Flujo editorial oficial: `revision-orquestador-editorial`.

## Estructura canonica de libro

```text
library/<ruta-nodos>/.../<book-node>/
  01.json
  01.pdf                  # opcional referencia
  img_<uuid>_<slug>.png   # alternativas de imagen
  02.json
library/_inbox/           # propuestas de entrada (NN.md, NN.pdf)
library/_backups/         # opcional
```

## UI y rutas

- Shell SPA:
  - `/` redirige a `/biblioteca`
  - `/biblioteca`
  - `/biblioteca/<path>`
  - `/cuento/<path>`
- API JSON versionada:
  - `/api/v1/library/node`
  - `/api/v1/stories/<path>`
  - `/api/v1/stories/<path>/pages/<int>`
  - `/api/v1/stories/<path>/pages/<int>/slots/<slot>/alternatives`
  - `/api/v1/stories/<path>/pages/<int>/slots/<slot>/active`
  - `/api/v1/health`
- Media:
  - `/media/<path>`

## Frontend local

- Codigo fuente SPA: `frontend/`
- Build: salida a `app/static/spa/` (ignorada por git)
- Comandos:
  - `npm --prefix frontend ci`
  - `npm --prefix frontend run build`

## CLI vigente

- `python manage.py runserver`

## Trazabilidad

- Operacion: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
