---
name: revision-prompts-decision-interactiva
description: Resolver hallazgos de prompts en diálogo asistido, aplicando decisiones y preservando trazabilidad editorial.
---

# Skill: Prompts Decisión Interactiva

## Propósito

Aplicar decisiones editoriales sobre prompts con control por severidad.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`
- `story_id`
- `severity_band`
- `pass_index` (opcional, por defecto `1`)

## Protocolo conversacional obligatorio

1. Cargar hallazgos activos de prompts para la banda.
2. Presentar cada hallazgo con opciones de reescritura.
3. Solicitar decisión explícita:
   - `accepted`
   - `rejected`
   - `defer` (solo en `minor|info`).
4. Aplicar cambios aceptados en prompts `current`.
5. Resumir cambios realizados y pendientes.

## Criterios de salida

- Se actualiza `NN.choices.json`.
- Si hay decisiones aceptadas, se actualiza `NN.json` en prompts `current`.

## Errores y recuperación

- En bandas bloqueantes no se permite `defer`.
- Si decisión incompleta, no avanzar a contraste.
