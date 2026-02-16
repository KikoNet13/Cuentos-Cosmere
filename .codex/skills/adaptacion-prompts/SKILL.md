---
name: "adaptacion-prompts"
description: "Revisa y ajusta prompts visuales por severidad, con gate obligatorio sobre prompt.main y trazabilidad completa de decisiones."
---

# Skill: adaptacion-prompts

## Objetivo
- Revisar prompts por severidad con foco visual en `prompt.main`.
- Proponer alternativas IA y aplicar decisiones humanas.

## Script
- `scripts/prompts.py`

## Input CLI
- `--story-rel-path`
- `--severity` (`critical|major|minor|info`)
- `--target-age`
- `--apply-decision-json` (opcional)

## Output JSON
- Hallazgos en `prompt.main`.
- Propuestas por hallazgo.
- Decisiones aplicadas.
- Conteo de abiertos por severidad.

## Regla de gate visual
- El cierre editorial depende del estado de `prompt.main`.
- Slots no principales pueden existir, pero no bloquean el gate de esta fase.

