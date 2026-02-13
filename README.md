# Generador de cuentos ilustrados

Proyecto local para revisar, adaptar y publicar cuentos ilustrados con fuente de verdad en JSON por cuento.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canónico: un cuento por archivo `NN.json` dentro de un nodo libro.
- Cada `NN.json` guarda:
  - metadatos de cuento
  - páginas con `text.original` y `text.current`
  - imágenes por slot (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen con `active_id`
- Runtime sin SQLite: la app navega por escaneo directo de disco.
- Flujo editorial oficial: skill `revision-orquestador-editorial`.

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

## Guía rápida del flujo editorial

1. Prepara fuentes en `library/_inbox/<titulo-libro>/`.
2. Ejecuta contexto canónico:
   - `revision-contexto-canon`
3. Ejecuta cascada de texto por severidad:
   - `revision-texto-deteccion`
   - `revision-texto-decision-interactiva`
   - `revision-texto-contraste-canon`
4. Si texto converge en `critical|major`, ejecuta cascada de prompts:
   - `revision-prompts-deteccion`
   - `revision-prompts-decision-interactiva`
   - `revision-prompts-contraste-canon`
5. Para flujo completo automático por libro:
   - `revision-orquestador-editorial`
6. Revisa en webapp:
   - lectura: `/story/<ruta>?p=N`
   - editorial: `/story/<ruta>?p=N&editor=1`

Guía detallada: `docs/guia-orquestador-editorial.md`.

## Skills y propósito

- `revision-contexto-canon`: construye contexto jerárquico y glosario consolidado.
- `revision-texto-deteccion`: genera findings de texto por banda de severidad.
- `revision-texto-decision-interactiva`: aplica decisiones por finding de texto.
- `revision-texto-contraste-canon`: valida desvío de texto frente al canon.
- `revision-prompts-deteccion`: genera findings de prompts por banda de severidad.
- `revision-prompts-decision-interactiva`: aplica decisiones por finding de prompts.
- `revision-prompts-contraste-canon`: valida desvío de prompts frente al canon.
- `revision-orquestador-editorial`: ejecuta el pipeline completo de cascada por severidad.

## Sidecars de revisión

Por libro, el pipeline guarda artefactos en `library/<book_rel_path>/_reviews/`:

- `pipeline_state.json`
- `context_chain.json`
- `glossary_merged.json`
- `NN.findings.json`
- `NN.choices.json`
- `NN.contrast.json`
- `NN.passes.json`
- derivados opcionales para UI/editor: `NN.review.json`, `NN.review.md`, `NN.decisions.json`

## Comando CLI vigente

- `python manage.py runserver`

## Trazabilidad

- Operación: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
