# Generador de cuentos ilustrados

Proyecto local para preparar cuentos ilustrados con fuente de verdad en archivos Markdown y cache SQLite temporal para navegacion rapida.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canonico: un cuento por archivo `NN.md` dentro de un nodo libro.
- Formato de `NN.md`: `## Meta` + secciones `## Pagina NN` con `### Texto` y `### Prompts`.
- Requisitos de imagen: lista tipada `tipo/ref`.
- Glosario opcional por nodo en `meta.md` (`## Glosario`), con merge jerarquico raiz -> libro.
- Cache temporal: `db/library_cache.sqlite`.
- UI: lectura/copia de texto y prompts, subida o pegado de imagenes por slot.

## Estructura canonica de libro

```text
library/<ruta-nodos>/.../<book-node>/
  meta.md                  # opcional (incluye glosario de nodo)
  01.md
  01.pdf
  01-p01-principal.png
  01-p01-secundaria-01.png
  02.md
  02.pdf
  anclas.md
library/_pending/
library/_inbox/
```

## Comandos CLI vigentes

- `python manage.py rebuild-cache`
- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py inbox-parse --input <path> --book <book_rel_path> --story-id <NN>`
- `python manage.py inbox-review-validate --batch-id <id>`
- `python manage.py inbox-apply --batch-id <id> --approve`
- `python manage.py inbox-apply --batch-id <id> --approve --force --force-reason "<motivo>"`
- `python manage.py runserver`

## Flujo recomendado

1. Si hay layout legacy, ejecutar `python manage.py migrate-library-layout --apply`.
2. Dejar fuente `.md` en `library/_pending/`.
3. Ingerir nuevo material con `inbox-parse`.
4. Revisar `library/_inbox/<batch_id>/review.md`, `ai_context.json`, `review_ai.md` y `review_ai.json`.
5. Validar `review_ai.json` con `inbox-review-validate`.
6. Aplicar solo propuestas aprobadas con `inbox-apply --approve`.
7. Usar `--force --force-reason` solo para overrides excepcionales.
8. Levantar servidor solo cuando se solicite explicitamente: `python manage.py runserver`.

## Trazabilidad

- Operacion: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
