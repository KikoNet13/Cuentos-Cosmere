---
name: "adaptacion-texto"
description: "Detecta hallazgos de texto por severidad y aplica decisiones interactivas con propuestas IA (A/B/C) y opcion libre D."
---

# Skill: adaptacion-texto

## Objetivo
- Revisar texto de un cuento por severidad.
- Entregar hallazgos y propuestas editables.
- Aplicar decisiones y registrar trazabilidad.

## Script
- `scripts/texto.py`

## Input CLI
- `--story-rel-path`
- `--severity` (`critical|major|minor|info`)
- `--target-age`
- `--apply-decision-json` (opcional)

## Output JSON
- Hallazgos detectados para la severidad.
- Propuestas por hallazgo.
- Resultado de decisiones aplicadas.
- Conteo de hallazgos abiertos.

## Decisionado
- Cada hallazgo ofrece 1-3 propuestas IA.
- Siempre se permite opcion `D` (texto humano libre).
- Cada resolucion se registra en:
  - `NN.review.json`
  - `NN.decisions.log.jsonl`

