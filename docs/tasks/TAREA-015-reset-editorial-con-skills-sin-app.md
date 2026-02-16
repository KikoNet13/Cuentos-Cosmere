# TAREA-015-reset-editorial-con-skills-sin-app

## Metadatos

- ID de tarea: `TAREA-015-reset-editorial-con-skills-sin-app`
- Fecha: 16/02/26 10:51
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Reiniciar el sistema editorial para que la adaptación propuesta inbox -> versión definitiva viva solo en skills `adaptacion-*`, dejando `app/` exclusivamente para la webapp Flask.

## Contexto

- Existía lógica editorial en `app/editorial_orquestador.py` y skills `revision-*`.
- Se acordó una frontera estricta: scripts editoriales dentro de cada skill.
- Se definió un nuevo contrato de sidecars centrado en:
  - `NN.review.json`
  - `NN.decisions.log.jsonl`

## Plan

1. Eliminar skills legacy `revision-*` y retirar `app/editorial_orquestador.py`.
2. Crear skills `adaptacion-*` con scripts internos (`contexto`, `texto`, `prompts`, `cierre`, `orquestar`).
3. Implementar sidecar maestro nuevo y log de decisiones por hallazgo.
4. Actualizar documentación operativa (`AGENTS.md`, `README.md`, `app/README.md`) y trazabilidad.
5. Validar ejecución finita (`--help`, caso end-to-end) y cerrar en commit único.

## Decisiones

- Se mantiene Flask sin pipeline editorial activo dentro de `app/`.
- `target_age` queda obligatorio desde el arranque (`contexto`/`orquestar`).
- Orden de fases fijo: `contexto -> texto -> prompts -> cierre`.
- Orden de severidad fijo: `critical -> major -> minor -> info`.
- Se preserva la opción `D` libre humana al aplicar decisiones.
- Gate visual de cierre restringido a `prompt.main`.

## Cambios aplicados

- Eliminado `app/editorial_orquestador.py`.
- Eliminadas skills legacy en repo:
  - `.codex/skills/revision-contexto-canon/`
  - `.codex/skills/revision-orquestador-editorial/`
  - `.codex/skills/revision-texto-*/`
  - `.codex/skills/revision-prompts-*/`
- Eliminada skill local:
  - `C:/Users/Kiko/.codex/skills/revision-adaptacion-editorial`
- Nuevas skills en repo:
  - `.codex/skills/adaptacion-contexto/`
  - `.codex/skills/adaptacion-texto/`
  - `.codex/skills/adaptacion-prompts/`
  - `.codex/skills/adaptacion-cierre/`
  - `.codex/skills/adaptacion-orquestador/`
- Nuevos scripts:
  - `.codex/skills/adaptacion-contexto/scripts/contexto.py`
  - `.codex/skills/adaptacion-texto/scripts/texto.py`
  - `.codex/skills/adaptacion-prompts/scripts/prompts.py`
  - `.codex/skills/adaptacion-cierre/scripts/cierre.py`
  - `.codex/skills/adaptacion-orquestador/scripts/orquestar.py`
  - `.codex/skills/adaptacion-orquestador/scripts/adaptacion_lib.py`
- Documentación actualizada:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `app/notebooklm_ingest.py` (mensaje de retirada)
  - `.gitignore` (ignora `library/`)

## Validación ejecutada

1. `python .codex/skills/adaptacion-contexto/scripts/contexto.py --help`
   - OK, ayuda mostrada.
2. `python .codex/skills/adaptacion-texto/scripts/texto.py --help`
   - OK, ayuda mostrada.
3. `python .codex/skills/adaptacion-prompts/scripts/prompts.py --help`
   - OK, ayuda mostrada.
4. `python .codex/skills/adaptacion-cierre/scripts/cierre.py --help`
   - OK, ayuda mostrada.
5. `python .codex/skills/adaptacion-orquestador/scripts/orquestar.py --help`
   - OK, ayuda mostrada.
6. `python -m py_compile` sobre los 6 scripts nuevos (`adaptacion_lib.py` + módulos)
   - OK, sin errores de sintaxis.
7. End-to-end:
   - `python .codex/skills/adaptacion-orquestador/scripts/orquestar.py --inbox-book-title "El imperio final" --book-rel-path "cosmere/nacidos-de-la-bruma-era-1/el-imperio-final" --target-age 8`
   - Resultado: se detectó `01.md`, se limpió sidecar legacy y el cuento quedó en `in_review` por 1 hallazgo `minor`.
8. Resolución de hallazgo + cierre:
   - `python .codex/skills/adaptacion-texto/scripts/texto.py --story-rel-path "cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/01" --severity minor --target-age 8 --apply-decision-json <archivo-json>`
   - `python .codex/skills/adaptacion-cierre/scripts/cierre.py --story-rel-path "cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/01"`
   - Resultado final: estado `definitive`, `open_counts` en cero y log generado en `01.decisions.log.jsonl`.
9. Reejecución integral:
   - `python .codex/skills/adaptacion-orquestador/scripts/orquestar.py --inbox-book-title "El imperio final" --book-rel-path "cosmere/nacidos-de-la-bruma-era-1/el-imperio-final" --target-age 8`
   - Resultado: `metrics.definitive = 1`, `metrics.in_review = 0`.

## Riesgos

- Los criterios semánticos de detección inicial son conservadores; puede requerir ajuste fino posterior para mayor cobertura editorial.

## Seguimiento

1. Afinar detectores por dominio canónico si se observan falsos negativos.
2. Añadir pruebas automáticas para scripts `adaptacion-*`.

## Commit asociado

- Mensaje de commit: `Tarea 015: reset editorial con skills sin app`
- Hash de commit: `pendiente`
