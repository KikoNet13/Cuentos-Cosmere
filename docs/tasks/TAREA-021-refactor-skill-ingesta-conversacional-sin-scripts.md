# TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts

## Metadatos

- ID de tarea: `TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts`
- Fecha: 17/02/26 11:02
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Refactorizar `.codex/skills/adaptacion-ingesta-inicial` para que la ingesta inicial sea 100% conversacional, sin scripts ni CLI, manteniendo contrato de salida en `NN.json`, `adaptation_context.json` y `NN.issues.json`.

## Alcance implementado

1. Eliminado el flujo CLI y el envelope ejecutable (`phase`, `pending_questions`, `planned_outputs`, etc.).
2. Reescrito `SKILL.md` con workflow conversacional completo:
   - descubrimiento de `NN.md` + `NN.pdf`;
   - gate canonico bloqueante por lote;
   - contraste con skill `pdf`;
   - preguntas una a una con opciones y excepcion de resolucion en bloque de incoherencias repetidas;
   - escritura incremental sobre archivos finales.
3. Actualizado `contracts.md` para conservar solo:
   - contrato de entradas/salidas;
   - reglas operativas de contraste;
   - protocolo conversacional;
   - tipos base de issues ampliables con justificacion.
4. Ajustado `agents/openai.yaml` al nuevo flujo sin scripts.
5. Eliminados artefactos `scripts/` de la skill.
6. Documentacion global alineada (`AGENTS.md`, `README.md`, `app/README.md`, `INDICE`, `CHANGELOG`).

## Decisiones

1. La skill no tiene scripts ni fallback CLI.
2. Bloqueo canonico inmediato por lote cuando falla cobertura PDF util de cualquier cuento.
3. Uso de skill `pdf` para contraste canonico.
4. Politica `md-first expandido` para glosario/contexto.
5. Preguntar todos los ambiguos (una pregunta por turno, con excepcion de resolucion en bloque por incoherencia repetida).
6. Escritura parcial directa en archivos finales con estado `in_review`/`pending`/`open` segun corresponda.

## Cambios aplicados

- Skill:
  - `.codex/skills/adaptacion-ingesta-inicial/SKILL.md`
  - `.codex/skills/adaptacion-ingesta-inicial/references/contracts.md`
  - `.codex/skills/adaptacion-ingesta-inicial/agents/openai.yaml`
  - eliminados:
    - `.codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py`
    - `.codex/skills/adaptacion-ingesta-inicial/scripts/__pycache__/ingesta_inicial.cpython-310.pyc`
- Documentacion:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/tasks/TAREA-021-refactor-skill-ingesta-conversacional-sin-scripts.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

1. `python C:/Users/Kiko/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/adaptacion-ingesta-inicial`
2. Verificacion de estructura:
   - ausencia de `.codex/skills/adaptacion-ingesta-inicial/scripts/`
   - coherencia de `SKILL.md`, `openai.yaml` y `references/contracts.md`.

## Riesgos y notas

1. Al no existir CLI, toda la ejecucion depende del protocolo conversacional correcto del agente.
2. Preguntar todos los ambiguos puede generar rondas largas en lotes grandes.
3. La calidad del contraste canonico depende del uso consistente de la skill `pdf` para evidencia.

## Commit asociado

- Mensaje de commit: `Tarea 021: skill de ingesta inicial 100% conversacional sin scripts`
- Hash de commit: pendiente
