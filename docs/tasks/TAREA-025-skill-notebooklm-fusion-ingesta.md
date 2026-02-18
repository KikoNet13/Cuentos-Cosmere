# TAREA-025 - Skill NotebookLM + fusion por partes en ingesta

- Fecha: 18/02/26 15:35
- Estado: cerrada
- Versión objetivo: 2.2.0

## Resumen

Se formaliza el tramo NotebookLM del flujo 3 IAs con una nueva skill conversacional (`notebooklm-comunicacion`) y se amplia `ingesta-cuentos` para aceptar piezas (`NN_a/_b`, fallback `a1/a2/b1/b2`), fusionarlas en memoria y archivar el inbox procesado en `_processed`.

## Alcance implementado

1. Nueva skill `notebooklm-comunicacion` (sin scripts):
   - setup de lote para NotebookLM;
   - prompts por partes `8+8` (`NN_a`, `NN_b`);
   - fallback automático `4+4` (`a1/a2/b1/b2`);
   - mensajes delta por archivo.
2. `ingesta-cuentos` actualizado:
   - descubrimiento de cuentos por `NN.json` o piezas;
   - fusion en memoria por combinaciones válidas;
   - validacion de rango por sufijo de parte;
   - warnings por cover discrepante;
   - archivado post-import en `library/_processed/<book_title>/<timestamp>/`.
3. Contrato de referencia extendido:
   - nuevos inputs de partes;
   - politicas de fusion y errores/warnings especificos (`input.pending_notebooklm`, `merge.*`).
4. Documentacion operativa actualizada:
   - `AGENTS.md`;
   - `README.md`;
   - guia breve orquestadora.

## Validaciones ejecutadas

1. `rg -n "notebooklm-comunicacion|NN_a|NN_b|_processed" AGENTS.md README.md .codex/skills docs/guia-orquestador-editorial.md`
   - resultado: referencias consistentes entre skill nueva, ingesta y docs.
2. `Get-Content -Raw .codex/skills/notebooklm-comunicacion/SKILL.md`
   - resultado: skill nueva con flujo, plantillas y fallback.
3. `Get-Content -Raw .codex/skills/ingesta-cuentos/SKILL.md`
   - resultado: incluye fusion en memoria, reglas de partes y archivado.

## Archivos principales tocados

- `AGENTS.md`
- `README.md`
- `docs/guia-orquestador-editorial.md`
- `.codex/skills/notebooklm-comunicacion/SKILL.md`
- `.codex/skills/notebooklm-comunicacion/agents/openai.yaml`
- `.codex/skills/ingesta-cuentos/SKILL.md`
- `.codex/skills/ingesta-cuentos/references/contracts.md`
- `.codex/skills/ingesta-cuentos/agents/openai.yaml`
- `docs/tasks/TAREA-025-skill-notebooklm-fusion-ingesta.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
