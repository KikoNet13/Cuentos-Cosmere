# Generador de cuentos ilustrados

Plataforma local para gestionar cuentos ilustrados con flujo 3 IAs:

1. Codex usa `notebooklm-comunicacion` para preparar prompts por partes (`NN_a/_b`, fallback `a1/a2/b1/b2`).
2. NotebookLM genera `NN.json` o partes + `meta.json` (opcional) en `_inbox`.
3. Codex usa `ingesta-cuentos` para fusionar en memoria, validar/importar y generar el dossier de ChatGPT Project por saga.
4. ChatGPT Project genera imágenes usando prompts/anchors.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato único por cuento: `NN.json` (dos digitos).
- Runtime de app sin SQLite (lectura directa de disco).
- Skills activas:
  - `.codex/skills/notebooklm-comunicacion/`
  - `.codex/skills/ingesta-cuentos/`
- Dossier operativo por saga:
  - `library/<book_rel_path>/chatgpt_project_setup.md` (setup de Project + flujo rapido de imagen).

## Contrato canónico

`NN.json` por cuento:

- top-level: `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
- página: `page_number`, `text`, `images`.
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

Imágenes por nodo:

- carpeta: `library/<node>/images/`
- índice: `library/<node>/images/index.json`
- nombre de asset: `<uuid>_<slug>.<ext>`

## Estructura esperada

```text
library/
  _inbox/
    <book_title>/
      01.json          # completo opcional
      02_a.json        # parte A (1..8)
      02_b.json        # parte B (9..16)
      02_a1.json       # fallback opcional
      02_a2.json
      02_b1.json
      02_b2.json
      meta.json        # opcional
  _processed/
    <book_title>/
      <timestamp>/
        ...            # copia archivada del inbox procesado
  meta.json            # global opcional
  <node>/.../<book>/
    01.json
    02.json
    meta.json          # opcional
    chatgpt_project_setup.md
    images/
      <uuid>_<slug>.png
      index.json
```

## UI

- Home biblioteca: `/`
- Ruta canónica de nodo/cuento: `/<ruta>`
- Lectura de cuento: `/<book>/<NN>?p=N` (sin `p`, página 1)
- Editor por página: `/<book>/<NN>?p=N&editor=1`
- Editor de portada: `/<book>/<NN>?editor=1`
- Fragmentos HTMX: `/<story_path>/_fr/*`
- Acciones editoriales: `/<story_path>/_act/*`
- Rutas legacy removidas: `/browse/*`, `/story/*`, `/editor/story/*`, `/n/*`.

## CLI de app

- `python manage.py runserver`

## Trazabilidad

- Operación: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
