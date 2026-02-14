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
3. Cargar `target_age` desde `adaptation_profile.json` y derivar umbrales activos para la banda.
4. Ejecutar detección de texto en la banda indicada.
5. Presentar resultados ordenados por:
   - severidad
   - página
   - categoría.
6. Para cada hallazgo mostrar:
   - evidencia
   - campo afectado
   - referencia canónica usada.
   - umbral de edad aplicado cuando corresponda.

## Criterios de salida

- Se genera o actualiza `NN.findings.json`.
- Los hallazgos de legibilidad/adaptación se calculan con el perfil de edad objetivo activo.
- El usuario recibe un listado priorizado de hallazgos listo para decidir.

## Errores y recuperación

- `severity_band` inválida: pedir banda correcta (`critical|major|minor|info`).
- `story_id` inexistente: pedir historia válida dentro del libro.
- Sin hallazgos: informar explícitamente y proponer avanzar al siguiente paso.
