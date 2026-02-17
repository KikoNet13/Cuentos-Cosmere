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
  - Ingesta inicial conversacional de `_inbox` a `NN.json` + sidecars con contraste canonico obligatorio contra `NN.pdf`.
  - Sin scripts ni CLI: el agente ejecuta todo el flujo en chat.
  - Si falta senal textual suficiente de historia en PDF canonico, la skill bloquea el lote completo.
  - Paginas visuales sin texto (portada/mapa) no bloquean por si solas.
  - Glosario/contexto en modo `md-first expandido` (el PDF aporta terminos solo para resolver incoherencias reales).
  - Soporte de contexto jerarquico por nodos (`book` + ancestros + global).
  - Contraste canonico con apoyo de la skill `pdf`.

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
