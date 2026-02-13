# TAREA-011-orquestador-editorial-skills-ui-minimal

## Metadatos

- ID de tarea: `TAREA-011-orquestador-editorial-skills-ui-minimal`
- Fecha: 13/02/26 16:24
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Implementar el pipeline editorial con skills encadenadas, sidecars de revisión por libro/cuento y UI minimal de lectura con modo editorial oculto por query.

## Contexto

La skill `revision-orquestador-editorial` cubría principalmente la ingesta inicial a `NN.json`, pero faltaba el flujo completo de filtros sucesivos (texto y prompts) con gating, decisiones manuales registradas y trazabilidad operativa.

## Plan

1. Implementar módulo de pipeline editorial con descubrimiento, ingesta, auditoría y corrección.
2. Separar UI en modo lectura por defecto y modo editorial bajo `editor=1`.
3. Crear familia de skills especializadas y skill orquestadora.
4. Mantener compatibilidad con `revision-orquestador-editorial` como alias.
5. Actualizar documentación y trazabilidad.

## Decisiones

- Exclusión de fuentes por carpeta `_ignore`.
- Prioridad de duplicados `NN.md`: archivo en raíz del libro.
- Sidecars operativos en `library/<book>/_reviews/`.
- Gate por criticidad: bloquear por hallazgos `critical|major`.
- Gate por libro: detener en el primer cuento bloqueado.
- Estado de cuento por etapas: `draft`, `text_reviewed|text_blocked`, `prompt_reviewed|prompt_blocked`, `ready`.
- UI de lectura minimal por defecto; editor solo bajo `?editor=1`.

## Cambios aplicados

- Pipeline editorial:
  - `app/editorial_orquestador.py` (nuevo en esta tarea)
  - `app/story_store.py` (utilidades `save_story_payload`, `set_story_status` y estados válidos)
- UI y rutas:
  - `app/routes_v3.py`
  - `app/templates/cuento_read.html`
  - `app/templates/cuento_editor.html`
  - `app/static/css/app.css`
- Documentación:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/context/INDICE.md`
  - `docs/tasks/TAREA-011-orquestador-editorial-skills-ui-minimal.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validación ejecutada

- Import del módulo editorial y pruebas de descubrimiento de fuentes.
- Verificación de lectura/editor en rutas Flask con `editor=1`.
- Compilación: incidente puntual por permisos de `__pycache__` en entorno local.

## Riesgos

- El pipeline en primera corrida puede quedar bloqueado hasta completar decisiones pendientes.
- Las heurísticas de auditoría eran base v1 y requerían evolución por saga/libro.

## Seguimiento

1. Extender heurísticas semánticas de auditoría con reglas canónicas por universo.
2. Incorporar soporte de decisiones por lote para reducir fricción operativa.

## Commit asociado

- Mensaje de commit: `Tarea 011: orquestador editorial con skills encadenadas y UI minimal`
- Hash de commit: pendiente
