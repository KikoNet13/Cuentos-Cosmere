# TAREA-007-parser-ia-auditoria-terminologia

## Metadatos

- ID de tarea: `TAREA-007-parser-ia-auditoria-terminologia`
- Fecha: 12/02/26 22:29
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0005`, `0006`

## Objetivo

Implementar parser con auditoria IA asistida en `inbox-parse`, gate critico en `inbox-apply`, contrato de glosario jerarquico y comando de validacion de review IA.

## Contexto

El flujo previo generaba propuesta tecnica (`review.md`) pero no tenia contrato estructurado para revisar coherencia semantica/canon/terminologia ni para bloquear aplicacion por hallazgos criticos.

## Plan

1. Extender parser para generar contexto y review IA estructurada por batch.
2. Incorporar validador CLI de `review_ai.json`.
3. Aplicar gate critico en `inbox-apply` con override trazable (`--force-reason`).
4. Documentar contratos (`meta.md` glosario, flujo de revision IA).
5. Actualizar skill operativa global y trazabilidad repo.

## Decisiones

- Auditoria IA en modo `codex_chat_manual` (sin API externa en CLI).
- Gate de `inbox-apply` bloquea por `status` pendiente/bloqueado y por `critical_open > 0`.
- `--force` exige `--force-reason` y registra override en `manifest.json`.
- Glosario por nodo en `meta.md` con `## Glosario` en tabla tipada y merge jerarquico.
- Deteccion automatica inicial: variantes prohibidas de glosario se crean como findings `critical`.

## Cambios aplicados

- Codigo:
  - `app/notebooklm_ingest.py`
  - `manage.py`
  - `Pipfile`
- Documentacion operativa:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
- ADR:
  - `docs/adr/0006-parser-ia-asistida-gate-critico.md`
  - `docs/adr/INDICE.md`
- Sistema de tareas:
  - `docs/tasks/TAREA-007-parser-ia-auditoria-terminologia.md`
  - `docs/tasks/INDICE.md`
- Changelog:
  - `CHANGELOG.md`
- Skill global:
  - `C:/Users/Kiko/.codex/skills/notebooklm-ingest/SKILL.md`
  - `C:/Users/Kiko/.codex/skills/notebooklm-ingest/references/checklist.md`
  - `C:/Users/Kiko/.codex/skills/notebooklm-ingest/references/auditoria.md`
  - `C:/Users/Kiko/.codex/skills/notebooklm-ingest/references/glosario.md`

## Validacion ejecutada

- `python manage.py --help`
- `python manage.py inbox-parse --help`
- `python manage.py inbox-review-validate --help`
- `python manage.py inbox-apply --help`
- `python -c "import ast,pathlib; ..."` (AST local de `manage.py` y `app/notebooklm_ingest.py`)
- `python manage.py inbox-parse --input "library\_pending\El imperio final\01.md" --book nacidos-de-la-bruma-era-1/el-imperio-final --story-id 07`
- `python manage.py inbox-review-validate --batch-id 20260212-212612-07`
- `python manage.py inbox-apply --batch-id 20260212-212612-07 --approve` (esperado: bloquea status pending)
- `python manage.py inbox-parse --input "library\_pending\El imperio final\01.md" --book nacidos-de-la-bruma-era-1/el-imperio-final --story-id 08`
- `python manage.py inbox-review-validate --batch-id 20260212-212646-08` con `review_ai.json` invalido (esperado: falla)
- `python manage.py inbox-parse --input "library\_pending\El imperio final\01.md" --book _inbox/test-book --story-id 01`
- `python manage.py inbox-apply --batch-id 20260212-212707-01 --approve --force` (esperado: falla sin reason)
- `python manage.py inbox-apply --batch-id 20260212-212707-01 --approve --force --force-reason "Validacion manual externa"` (esperado: aplica)
- `python manage.py inbox-parse --input "library\_pending\El imperio final\01.md" --book _inbox/test-book --story-id 02`
- `python manage.py inbox-apply --batch-id 20260212-212723-02 --approve` con `critical_open=1` (esperado: bloquea)
- `python manage.py inbox-review-validate --batch-id 20260212-212723-02` con `critical_open=0` (esperado: no bloquea)
- `python manage.py inbox-apply --batch-id 20260212-212723-02 --approve` (esperado: aplica)
- `python manage.py inbox-parse --input "library\_pending\El imperio final\01.md" --book _inbox/test-hierarchy --story-id 03` + inspeccion de `review_ai.json` y `ai_context.json` (esperado: override jerarquico + finding critico por termino prohibido)

## Riesgos

- Si no se mantiene actualizado `review_ai.json`, el gate puede bloquear por `status=pending` aunque no existan criticos.
- Extraccion de PDF depende de `pypdf`; si no esta instalado, el parser deja warning y continua.
- El cache reconstruido puede reportar warnings de `_pending` por el contrato actual de deteccion de libros.

## Seguimiento

1. Definir politica para excluir `_pending` del escaneo de libros si se desea reducir ruido en warnings.
2. Publicar plantilla recomendada de `meta.md` con ejemplo de tabla `## Glosario`.
3. Evaluar un comando auxiliar para actualizar `review_ai.json` desde checklist interactiva.

## Commit asociado

- Mensaje de commit: `Tarea 007: parser IA asistida y gate critico mixto`
- Hash de commit: `pendiente`
