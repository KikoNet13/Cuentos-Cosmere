---
name: "adaptacion-cierre"
description: "Valida el cierre editorial final del cuento y fija estado definitive solo si no quedan hallazgos abiertos."
---

# Skill: adaptacion-cierre

## Objetivo
- Ejecutar la validacion final del cuento.
- Aplicar estado final:
  - `definitive` si no hay abiertos.
  - `in_review` si queda cualquier hallazgo abierto.

## Script
- `scripts/cierre.py`

## Input CLI
- `--story-rel-path`

## Output JSON
- Estado final del cuento.
- `open_counts` por severidad.
- Bloqueos inyectados (si faltan texto/prompt.main).

