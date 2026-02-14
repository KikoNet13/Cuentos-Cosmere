---
name: revision-texto-contraste-canon
description: Contrastar texto revisado contra canon y glosario, identificando desvíos residuales y decisión de cierre o nueva pasada.
---

# Skill: Texto Contraste Canon

## Propósito

Evaluar si el texto revisado mantiene coherencia suficiente con el canon para cerrar banda o iterar.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`
- `story_id`
- `severity_band`

## Protocolo conversacional obligatorio

1. Validar inputs y contexto canónico vigente.
2. Ejecutar contraste de texto para la banda activa.
3. Informar alertas abiertas por página/campo.
4. Proponer decisión de continuación:
   - repetir ciclo detección-decisión en misma banda
   - cerrar banda y avanzar.
5. Si la banda es bloqueante (`critical|major`) y hay alertas, marcar estado de bloqueo.

## Criterios de salida

- Se genera o actualiza `NN.contrast.json`.
- Se emite estado de banda: `converged` o `requires_new_pass`.

## Errores y recuperación

- Si no hay referencia PDF: continuar con contraste parcial y avisar.
- Si hay alertas persistentes en banda bloqueante: impedir avance de etapa.
