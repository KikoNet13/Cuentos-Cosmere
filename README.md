# Generador de cuentos ilustrados

Proyecto local para revisar, adaptar y publicar cuentos ilustrados con fuente de verdad en JSON por cuento.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canónico: un cuento por archivo `NN.json` dentro de un nodo libro.
- `NN.json` guarda:
  - metadatos de cuento
  - páginas con `text.original` y `text.current`
  - imágenes por slot (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen con `active_id`
- Runtime de app sin SQLite: navegación por escaneo directo de disco.
- Frontera obligatoria:
  - `app/` solo webapp Flask de visualización/edición.
  - la adaptación editorial vive en skills `adaptacion-*` y sus scripts.

## Estructura canónica

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

## Flujo editorial oficial (skills)

Skills conversacionales:

1. `adaptacion-contexto`
2. `adaptacion-texto`
3. `adaptacion-prompts`
4. `adaptacion-cierre`
5. `adaptacion-orquestador`

Secuencia:

1. Resolver `target_age` (obligatorio).
2. `contexto` para inventario y perfil editorial.
3. `texto` por severidad (`critical -> major -> minor -> info`).
4. `prompts` por severidad (gate visual sobre `prompt.main`).
5. `cierre`:
   - `definitive` con cero hallazgos abiertos.
   - `in_review` si queda cualquiera abierto.

Cada hallazgo ofrece 1-3 propuestas IA y opción `D` libre humana.

## Sidecars de revisión

Por cuento en `library/<book_rel_path>/_reviews/`:

- `NN.review.json` (estado maestro del ciclo)
- `NN.decisions.log.jsonl` (una línea por hallazgo resuelto)

## UI

- Lectura: `/story/<ruta>?p=N`
- Editorial de página: `/story/<ruta>?p=N&editor=1`

## CLI de app

- `python manage.py runserver`

## Trazabilidad

- Operación: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`

