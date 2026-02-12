# Generador de cuentos ilustrados

Proyecto local para preparar cuentos ilustrados con fuente de verdad en archivos Markdown y caché SQLite temporal para navegación rápida.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canónico: un cuento por archivo `NN.md` dentro de un nodo libro.
- Formato de `NN.md`: `## Meta` + secciones `## Página NN` con `### Texto` y `### Prompts`.
- Requisitos de imagen: lista tipada `tipo/ref`.
- Caché temporal: `db/library_cache.sqlite`.
- UI: lectura/copia de texto y prompts, subida o pegado de imágenes por slot.

## Estructura canónica de libro

```text
library/<ruta-nodos>/.../<book-node>/
  01.md
  01.pdf
  01-p01-principal.png
  01-p01-secundaria-01.png
  02.md
  02.pdf
  anclas.md
  _inbox/
```

## Comandos CLI vigentes

- `python manage.py rebuild-cache`
- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py inbox-parse --input <path> --book <book_rel_path> --story-id <NN>`
- `python manage.py inbox-apply --batch-id <id> --approve`
- `python manage.py runserver`

## Flujo recomendado

1. Si hay layout legacy, ejecutar `python manage.py migrate-library-layout --apply`.
2. Ingerir nuevo material con `inbox-parse` y revisar `library/_inbox/<batch_id>/review.md`.
3. Aplicar solo propuestas aprobadas con `inbox-apply --approve`.
4. Levantar servidor solo cuando se solicite explícitamente: `python manage.py runserver`.

## Trazabilidad

- Operación: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
