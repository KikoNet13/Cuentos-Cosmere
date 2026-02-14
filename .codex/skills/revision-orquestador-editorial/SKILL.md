---
name: revision-orquestador-editorial
description: Orquestar de forma conversacional el ciclo completo por severidad (texto y prompts), con gates y trazabilidad sidecar.
---

# Skill: Orquestador Editorial

## Propósito

Coordinar el flujo editorial completo de un libro en modo asistido e interactivo.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`

## Protocolo conversacional obligatorio

1. Confirmar inputs y alcance del libro.
2. Ejecutar contexto e ingesta inicial.
   - Si existe `context_review.json`, se consume automáticamente para usar el glosario efectivo.
   - No dispara revisión ligera de contexto por sí mismo; esa revisión se realiza desde `revision-contexto-canon`.
3. Etapa texto por severidad:
   - detección
   - decisión
   - contraste
   - repetición por pasadas hasta converger o bloquear.
4. Si texto converge en bandas bloqueantes, ejecutar etapa prompts con el mismo ciclo.
5. Detener libro en el primer cuento bloqueado y explicitar causa.
6. Cerrar con resumen:
   - cuentos aprobados
   - cuentos bloqueados
   - métricas por severidad.

## Criterios de salida

- `pipeline_state.json` actualizado con fase y convergencia.
- Sidecars por cuento y libro actualizados según contrato.
- Estado final por cuento (`ready`, `text_blocked`, `prompt_blocked`).

## Errores y recuperación

- Si un cuento bloquea en `critical|major`, no continuar con el siguiente.
- Si faltan fuentes válidas en inbox, detener con mensaje de inventario vacío.
