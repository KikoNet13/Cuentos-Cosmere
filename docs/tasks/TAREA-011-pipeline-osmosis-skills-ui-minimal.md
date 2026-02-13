# TAREA-011-pipeline-osmosis-skills-ui-minimal

## Metadatos

- ID de tarea: `TAREA-011-pipeline-osmosis-skills-ui-minimal`
- Fecha: 13/02/26 16:24
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Implementar el pipeline editorial "osmosis" con skills encadenadas, sidecars de revision por libro/cuento y UI minimal de lectura con modo editorial oculto por query.

## Contexto

La skill `revision-adaptacion-editorial` cubria principalmente la ingesta inicial a `NN.json`, pero faltaba el flujo completo de filtros sucesivos (texto y prompts) con gating, decisiones manuales registradas y trazabilidad operativa.

## Plan

1. Implementar modulo de pipeline editorial con descubrimiento, ingesta, auditoria y correccion.
2. Separar UI en modo lectura por defecto y modo editorial bajo `editor=1`.
3. Crear familia de skills especializadas + skill orquestadora.
4. Mantener compatibilidad con `revision-adaptacion-editorial` como alias.
5. Actualizar documentacion y trazabilidad.

## Decisiones

- Exclusion de fuentes por carpeta `_ignore`.
- Prioridad de duplicados `NN.md`: archivo en raiz del libro.
- Sidecars operativos en `library/<book>/_reviews/`.
- Gate por criticidad: bloquear por hallazgos `critical|major`.
- Gate por libro: detener en el primer cuento bloqueado.
- Estado de cuento por etapas: `draft`, `text_reviewed|text_blocked`, `prompt_reviewed|prompt_blocked`, `ready`.
- UI de lectura minimal por defecto; editor solo bajo `?editor=1`.

## Cambios aplicados

- Pipeline editorial:
  - `app/editorial_osmosis.py` (nuevo)
  - `app/story_store.py` (nuevas utilidades `save_story_payload`, `set_story_status` y estados validos)
- UI y rutas:
  - `app/routes_v3.py`
  - `app/templates/cuento_read.html` (nuevo)
  - `app/templates/cuento_editor.html` (nuevo)
  - `app/static/css/app.css`
- Skills nuevas:
  - `.codex/skills/revision-ingesta-json/SKILL.md`
  - `.codex/skills/revision-auditoria-texto/SKILL.md`
  - `.codex/skills/revision-correccion-texto/SKILL.md`
  - `.codex/skills/revision-auditoria-prompts/SKILL.md`
  - `.codex/skills/revision-correccion-prompts/SKILL.md`
  - `.codex/skills/revision-osmosis-orquestador/SKILL.md`
- Compatibilidad:
  - `.codex/skills/revision-adaptacion-editorial/SKILL.md` (alias operativo al pipeline osmosis)
- Documentacion:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/context/INDICE.md`
  - `docs/tasks/TAREA-011-pipeline-osmosis-skills-ui-minimal.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

- `python -c "import app.editorial_osmosis as eo; print(...)"` (import y constantes OK).
- `python -c "... discover_inbox_stories(...)"` (selecciona `01-03`, ignora `_ignore`).
- `python -c "... Flask test_client GET /story/... y /story/...&editor=1"`:
  - lectura sin formularios de guardado
  - editor con formularios y enlace de retorno a lectura.
- `python -m compileall app manage.py`:
  - fallo por permisos de escritura en `__pycache__` del entorno (sin impacto funcional en validaciones anteriores).

## Riesgos

- El pipeline en primera corrida puede quedar bloqueado hasta que se completen decisiones en `NN.decisions.json`.
- Las heuristicas de auditoria son base v1 y pueden requerir refinamiento por saga/libro.

## Seguimiento

1. Extender heuristicas semanticas de auditoria con reglas canonicas por universo.
2. Incorporar soporte de lotes de decisiones por pagina para reducir friccion operativa.

## Commit asociado

- Mensaje de commit: `Tarea 011: pipeline osmosis con skills encadenadas y UI minimal`
- Hash de commit: pendiente
