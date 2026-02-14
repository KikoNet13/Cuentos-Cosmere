---
name: revision-texto-decision-interactiva
description: Guiar decisiones por hallazgo de texto en modo interactivo (opciones A/B/C), aplicando cambios aceptados con trazabilidad.
---

# Skill: Texto Decisión Interactiva

## Propósito

Convertir hallazgos de texto en decisiones editoriales aplicadas y registradas.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`
- `story_id`
- `severity_band`
- `pass_index` (opcional, por defecto `1`)

## Protocolo conversacional obligatorio

1. Cargar hallazgos de la banda/pasada activa.
2. Recorrer hallazgos uno a uno, mostrando:
   - evidencia
   - impacto narrativo estimado
   - opciones propuestas.
3. Solicitar decisión explícita por hallazgo:
   - `accepted`
   - `rejected`
   - `defer` (solo en `minor|info`).
4. Aplicar cambios aceptados sobre `text.current`.
5. Confirmar resumen de decisiones y cambios aplicados.

## Criterios de salida

- Se actualiza `NN.choices.json`.
- Si hubo aceptaciones, se actualiza `NN.json` en `text.current`.
- Queda trazabilidad lista para contraste.

## Errores y recuperación

- En `critical|major`, `defer` no es válido: forzar resolución.
- Si falta opción seleccionada en `accepted`: pedir selección antes de continuar.
- Si no hay hallazgos activos: avisar y proponer pasar a contraste.
