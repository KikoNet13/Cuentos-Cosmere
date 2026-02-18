# 0006 - Parser con auditoria IA asistida y gate critico mixto

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

El flujo `inbox-parse` generaba propuesta estructural, pero la revisión semantica (canon, terminologia, coherencia texto/prompt) quedaba totalmente manual y sin contrato técnico para bloquear `inbox-apply`.

## Decision

Se adopta un esquema de auditoria IA asistida por Codex (sin API externa) con los siguientes contratos:

- `inbox-parse` genera artefactos adicionales por batch:
  - `ai_context.json`
  - `review_ai.md`
  - `review_ai.json`
- `review_ai.json` usa esquema estructurado con:
  - `status`: `pending|approved|blocked|approved_with_warnings`
  - `review_mode`: `codex_chat_manual`
  - `findings[]` tipado (`severity`, `category`, `state`, evidencia y fix)
  - `metrics` (`critical_open`, `major_open`, `minor_open`, `info_open`)
- `inbox-review-validate` válida esquema y consistencia.
- `inbox-apply` aplica gate IA por defecto:
  - bloquea si falta o es invalido `review_ai.json`
  - bloquea si `status` es `pending|blocked`
  - bloquea si `critical_open > 0`
- Override mixto:
  - `--force` solo válido con `--force-reason`
  - el override queda trazado en `manifest.json`.
- Se define glosario jerarquico opcional por nodo en `meta.md` (`## Glosario`) con tabla:
  - `termino|canonico|permitidas|prohibidas|notas`
  - merge raiz -> libro, con override del nodo más especifico.

## Consecuencias

- La ingestion mantiene automatizacion técnica y agrega trazabilidad semantica.
- El bloqueo por criticos protege el canon sin impedir overrides explicitamente justificados.
- Se habilita deteccion automática inicial de variantes prohibidas de glosario.
- La revisión semantica sigue siendo asistida por Codex en chat (sin dependencia de API externa en CLI).
