---
name: revision-adaptacion-editorial
description: Alias operativo compatible del flujo editorial. Redirige al pipeline osmosis por skills encadenadas (ingesta, auditoria/correccion de texto y prompts, gates por criticidad y cierre por libro).
---

# Alias Revision Adaptacion Editorial

Esta skill se mantiene por compatibilidad con flujos existentes.

## Encadenado oficial

1. `revision-osmosis-orquestador` para flujo completo por libro.
2. `revision-ingesta-json` para solo fase de ingesta.
3. `revision-auditoria-texto` y `revision-correccion-texto`.
4. `revision-auditoria-prompts` y `revision-correccion-prompts`.

## Regla

- Priorizar el uso de `revision-osmosis-orquestador`.
- Usar sub-skills de forma aislada cuando se requiera control fino por fase.

## Referencias

- `references/checklist.md`
- `references/esquema-json.md`
- `references/revision-editorial.md`
