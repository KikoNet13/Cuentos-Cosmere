---
name: revision-contexto-canon
description: Preparar contexto canónico por libro para revisión editorial asistida (sin comandos), consolidando referencias y glosario operativo.
---

# Skill: Contexto Canon

## Propósito

Construir el contexto canónico de un libro para iniciar el flujo editorial interactivo.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`

## Protocolo conversacional obligatorio

1. Pedir o confirmar `inbox_book_title` y `book_rel_path`.
2. Validar que el libro existe en `library/_inbox/<inbox_book_title>/`.
3. Ejecutar internamente la construcción de contexto.
4. Resumir al usuario:
   - PDFs canónicos detectados
   - archivos de contexto jerárquico usados
   - tamaño del glosario consolidado.
5. Ejecutar subfase opcional de revisión interactiva ligera del glosario:
   - Mostrar por término: `term`, `canonical`, `allowed`, `forbidden`, `source_rel`.
   - Solicitar decisión explícita: `accepted`, `rejected`, `defer`, `pending`.
   - Si `accepted`, permitir:
     - `preferred_alias` (opcional)
     - `allowed_add[]`
     - `forbidden_add[]`
     - `notes`.
   - Persistir decisiones en `context_review.json`.
   - Regenerar `glossary_merged.json` efectivo aplicando solo decisiones `accepted`.
6. Confirmar que se puede pasar a detección de texto.

## Criterios de salida

- Se generan o actualizan:
  - `context_chain.json`
  - `glossary_merged.json`
  - `context_review.json` (solo si se ejecuta revisión ligera)
- Se entrega un resumen legible para revisión editorial.

## Errores y recuperación

- Si falta el libro en inbox: pedir corrección del título/ruta.
- Si no hay PDFs canónicos: continuar, avisando que el contraste será limitado.
- Si el glosario está vacío: continuar, avisando que no habrá reglas terminológicas.
- Si una decisión referencia un término inexistente: registrar en `metrics.ignored_missing_term` y continuar.
