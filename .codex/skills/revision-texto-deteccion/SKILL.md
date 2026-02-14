---
name: revision-texto-deteccion
description: Detectar incoherencias y hallazgos de texto por severidad en modo conversacional, priorizando contexto y canon.
---

# Skill: Texto Detección

## Propósito

Detectar hallazgos en `text.current` para una historia y una banda de severidad.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`
- `story_id`
- `severity_band`
- `pass_index` (opcional, por defecto `1`)

## Protocolo conversacional obligatorio

1. Confirmar inputs y validar formato (`story_id=NN`, severidad válida).
2. Asegurar contexto canónico actualizado para el libro.
3. Ejecutar detección de texto en la banda indicada.
4. Presentar resultados ordenados por:
   - severidad
   - página
   - categoría.
5. Para cada hallazgo mostrar:
   - evidencia
   - campo afectado
   - referencia canónica usada.

## Criterios de salida

- Se genera o actualiza `NN.findings.json`.
- El usuario recibe un listado priorizado de hallazgos listo para decidir.

## Errores y recuperación

- `severity_band` inválida: pedir banda correcta (`critical|major|minor|info`).
- `story_id` inexistente: pedir historia válida dentro del libro.
- Sin hallazgos: informar explícitamente y proponer avanzar al siguiente paso.
