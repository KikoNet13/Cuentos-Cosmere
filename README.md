# Generador de cuentos ilustrados

Proyecto local para revisar y publicar cuentos ilustrados con fuente de verdad en JSON por cuento.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canonico: un cuento por archivo `NN.json` dentro de un nodo libro.
- `NN.json` guarda:
  - metadatos de cuento
  - paginas con `text.original` y `text.current`
  - imagenes por slot (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen con `active_id`
- Runtime sin SQLite: navegacion por escaneo directo de disco.
- Frontera obligatoria:
  - `app/` solo webapp Flask de visualizacion/edicion.
  - pipeline editorial fuera de `app/` y fuera de este repositorio.

## Estructura canonica

```text
library/<ruta-nodos>/.../<book-node>/
  01.json
  img_<uuid>_<slug>.png   # alternativas de imagen
  02.json
  _reviews/
    01.review.json
    01.decisions.log.jsonl
library/_inbox/           # propuestas de entrada (NN.md, NN.pdf)
library/_backups/         # opcional
```

## UI

- Lectura: `/story/<ruta>?p=N`
- Edicion de pagina: `/story/<ruta>?p=N&editor=1`

## CLI de app

- `python manage.py runserver`

## Trazabilidad

- Operacion: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
