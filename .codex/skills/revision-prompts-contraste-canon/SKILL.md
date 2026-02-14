---
name: revision-prompts-contraste-canon
description: Contrastar prompts revisados contra canon y continuidad para decidir convergencia o nueva pasada.
---

# Skill: Prompts Contraste Canon

## Propósito

Confirmar que los prompts revisados son coherentes con texto, canon y continuidad visual.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`
- `story_id`
- `severity_band`

## Protocolo conversacional obligatorio

1. Validar contexto y estado de la historia.
2. Ejecutar contraste de prompts para la banda activa.
3. Mostrar alertas por página, con su severidad.
4. Decidir con el usuario:
   - repetir pasada
   - cerrar banda y avanzar.
5. Aplicar gate en `critical|major` si no converge.

## Criterios de salida

- Se actualiza `NN.contrast.json`.
- Se informa convergencia o necesidad de nueva pasada.

## Errores y recuperación

- Si no existe `story_id` en el libro: pedir historia válida.
- Si faltan prompts en páginas críticas: mantener banda bloqueada.
