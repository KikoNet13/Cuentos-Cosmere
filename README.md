# Generador de cuentos ilustrados

Plataforma local para gestionar cuentos ilustrados con flujo 3 IAs:

1. NotebookLM genera `NN.json` y `meta.json` (opcional) en `_inbox`.
2. Codex valida/importa y mantiene la app.
3. ChatGPT Project genera imagenes usando prompts/anchors.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato unico por cuento: `NN.json` (dos digitos).
- Runtime de app sin SQLite (lectura directa de disco).
- Skill de ingesta activa: `.codex/skills/ingesta-cuentos/` (conversacional, sin scripts).

## Contrato canonico

`NN.json` por cuento:

- top-level: `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
- pagina: `page_number`, `text`, `images`.
- slot de imagen (`cover`, `images.main`, `images.secondary` opcional):
  - `status`, `prompt`, `active_id`, `alternatives[]`, `reference_ids[]` opcional.
- alternativa:
  - `id` (filename), `slug`, `asset_rel_path`, `mime_type`, `status`, `created_at`, `notes`.

`meta.json` por nodo (global + ancestros + libro):

- rutas:
  - `library/meta.json`
  - `library/<node>/meta.json`
- minimos:
  - `collection.title`, `anchors[]`, `updated_at`.

Imagenes por nodo:

- carpeta: `library/<node>/images/`
- indice: `library/<node>/images/index.json`
- nombre de asset: `<uuid>_<slug>.<ext>`

## Estructura esperada

```text
library/
  _inbox/
    <book_title>/
      01.json
      02.json
      meta.json        # opcional
  meta.json            # global opcional
  <node>/.../<book>/
    01.json
    02.json
    meta.json          # opcional
    images/
      <uuid>_<slug>.png
      index.json
```

## UI

- Home biblioteca: `/`
- Ruta canonica de nodo/cuento: `/<ruta>`
- Lectura de cuento: `/<book>/<NN>?p=N` (sin `p`, pagina 1)
- Editor por pagina: `/<book>/<NN>?p=N&editor=1`
- Editor de portada: `/<book>/<NN>?editor=1`
- Fragmentos HTMX: `/<story_path>/_fr/*`
- Acciones editoriales: `/<story_path>/_act/*`
- Rutas legacy removidas: `/browse/*`, `/story/*`, `/editor/story/*`, `/n/*`.

## CLI de app

- `python manage.py runserver`

## Trazabilidad

- Operacion: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
