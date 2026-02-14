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
- Runtime sin SQLite: la app navega por escaneo directo de disco.
- Flujo editorial oficial: `revision-orquestador-editorial`.

## Estructura canónica de libro

```text
library/<ruta-nodos>/.../<book-node>/
  01.json
  01.pdf                  # opcional referencia
  img_<uuid>_<slug>.png   # alternativas de imagen
  02.json
library/_inbox/           # propuestas de entrada (NN.md, NN.pdf)
library/_backups/         # opcional
```

## Uso editorial (modo conversacional)

Las skills son de agente: se usan en diálogo interactivo contigo, sin comandos embebidos.

### Secuencia recomendada

1. `revision-contexto-canon`
   - opcional: revisión ligera de terminología y sidecar `context_review.json`.
2. `revision-texto-deteccion`
3. `revision-texto-decision-interactiva`
4. `revision-texto-contraste-canon`
5. `revision-prompts-deteccion`
6. `revision-prompts-decision-interactiva`
7. `revision-prompts-contraste-canon`
8. `revision-orquestador-editorial` (flujo integral por libro)

## Sidecars de revisión

Por libro, el pipeline guarda artefactos en `library/<book_rel_path>/_reviews/`:

- `pipeline_state.json`
- `context_chain.json`
- `glossary_merged.json`
- `context_review.json` (opcional, generado por revisión ligera manual)
- `NN.findings.json`
- `NN.choices.json`
- `NN.contrast.json`
- `NN.passes.json`
- derivados opcionales para UI/editor:
  - `NN.review.json`
  - `NN.review.md`
  - `NN.decisions.json`

## UI

- Lectura: `/story/<ruta>?p=N`
- Editorial (solo ajustes puntuales): `/story/<ruta>?p=N&editor=1`

## CLI vigente

- `python manage.py runserver`

## Trazabilidad

- Operación: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
