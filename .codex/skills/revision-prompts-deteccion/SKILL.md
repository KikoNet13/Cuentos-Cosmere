---
name: revision-prompts-deteccion
description: Detectar hallazgos en prompts por severidad, validando estructura y coherencia visual con el texto revisado.
---

# Skill: Prompts Detección

## Propósito

Detectar incoherencias en `images.main.prompt.current` y preparar la toma de decisiones.

## Inputs requeridos

- `inbox_book_title`
- `book_rel_path`
- `story_id`
- `severity_band`
- `pass_index` (opcional, por defecto `1`)

## Protocolo conversacional obligatorio

1. Confirmar que texto no está bloqueado en `critical|major`.
2. Validar inputs (`story_id`, `severity_band`, `pass_index`).
3. Cargar `target_age` desde `adaptation_profile.json` y umbrales visuales activos.
4. Ejecutar detección de prompts para la banda activa.
5. Presentar hallazgos por página con evidencia y prioridad.
6. Preparar transición a decisión interactiva.

## Criterios de salida

- Se actualiza `NN.findings.json` para etapa `prompt`.
- Los hallazgos se contextualizan con perfil de edad objetivo activo.
- Se entrega listado priorizado para decisión.

## Errores y recuperación

- Si texto está bloqueado: no permitir iniciar prompts.
- Si la plantilla estructurada v1 falta: registrar como hallazgo `major`.
