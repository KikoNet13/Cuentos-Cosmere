# TAREA-012-cascada-editorial-severidad-tres-skills

## Metadatos

- ID de tarea: `TAREA-012-cascada-editorial-severidad-tres-skills`
- Fecha: 13/02/26 18:40
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Implementar una cascada editorial por severidad (`critical -> major -> minor -> info`) con ciclo de 3 skills por nivel (detección, decisión interactiva y contraste con canon), en dos etapas (`text` y `prompt`), con convergencia por pasadas y tope por severidad.

## Alcance implementado

1. Contexto jerárquico por ruta de libro y glosario consolidado.
2. Canon principal por PDFs de `library/_inbox/<libro>/`.
3. Etapa de texto con cascada por severidad.
4. Etapa de prompts condicionada a convergencia de texto en `critical|major`.
5. Sidecars nuevos por cuento y por libro para trazabilidad de pasadas.
6. Estado de pipeline extendido con banda de severidad, pasada y convergencia.
7. Documentación de uso y operación actualizada.

## Decisiones

- `_ignore` se mantiene como exclusión estricta de fuentes de ingesta.
- Duplicados `NN.md` priorizan archivo en raíz del libro.
- Tope por severidad:
  - `critical`: 5
  - `major`: 4
  - `minor`: 3
  - `info`: 2
- `critical|major` bloquean cierre de etapa/libro si no convergen.
- `minor|info` no bloquean cierre global si ya tienen decisión explícita.
- Se conservan sidecars legacy (`NN.review.json|md`, `NN.decisions.json`) como salida derivada para UI/editor.

## Cambios aplicados

- Lógica editorial:
  - `app/editorial_orquestador.py`
- Documentación:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/guia-orquestador-editorial.md`
  - `docs/context/INDICE.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Sidecars incorporados

Por libro:

- `library/<book_rel_path>/_reviews/context_chain.json`
- `library/<book_rel_path>/_reviews/glossary_merged.json`
- `library/<book_rel_path>/_reviews/pipeline_state.json`

Por cuento:

- `NN.findings.json`
- `NN.choices.json`
- `NN.contrast.json`
- `NN.passes.json`

## Validación ejecutada

1. `python -m py_compile app/editorial_orquestador.py`
2. `python -c "import app.editorial_orquestador as eo; print(hasattr(eo, 'run_orquestador_editorial'))"`
3. Búsquedas de consistencia:
   - `rg -n "revision-adaptacion-editorial|editorial_orquestador" -S .`
   - `rg -n "[\\x{00C3}\\x{00C2}\\x{FFFD}]" -S docs/tasks/INDICE.md docs/tasks/TAREA-011-orquestador-editorial-skills-ui-minimal.md`

## Riesgos y notas

1. La edición de contenidos bajo `.codex/skills/` está bloqueada en esta sesión por ACL (`Access denied`), por lo que el alta/baja final de skills locales puede requerir ejecución manual en terminal del usuario.
2. El contraste con canon es heurístico (v1) y debe evolucionar con reglas por saga/libro.

## Commit asociado

- Mensaje de commit: `Tarea 012: cascada editorial por severidad con ciclo detección-decisión-contraste`
- Hash de commit: pendiente
