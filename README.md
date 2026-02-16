# Generador de cuentos ilustrados

Proyecto local para revisar y publicar cuentos ilustrados con fuente de verdad en JSON por cuento.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canonico: un cuento por archivo `NN.json` dentro de un nodo libro.
- `NN.json` guarda:
  - metadatos de cuento
  - metadatos de ingesta inicial (`story_title`, `cover`, `source_refs`, `ingest_meta`)
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
    adaptation_context.json
    01.issues.json
    01.review.json
    01.decisions.log.jsonl
library/_inbox/           # propuestas de entrada (NN.md, NN.pdf)
library/_backups/         # opcional
```

## Skills versionadas

- `.codex/skills/adaptacion-ingesta-inicial/`
  - Ingesta inicial interactiva de `_inbox` a `NN.json` + sidecars.
  - Script: `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --help`

## UI

- Stack: Jinja + Bulma + HTMX.
- Home biblioteca: `/`
- Navegacion de nodos: `/browse/<ruta>`
- Lectura por pagina: `/story/<ruta>/page/<N>`
- Edicion por pagina: `/editor/story/<ruta>/page/<N>`
- Fragmentos HTMX de lectura: `/fragments/story/<ruta>/page/<N>/...`
- Compatibilidad legacy con redirect:
  - `/n/<ruta>`
  - `/story/<ruta>?p=N`
  - `/story/<ruta>?p=N&editor=1`

## CLI de app

- `python manage.py runserver`

## Trazabilidad

- Operacion: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
