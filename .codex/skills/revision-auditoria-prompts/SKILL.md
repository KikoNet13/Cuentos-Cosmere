---
name: revision-auditoria-prompts
description: Auditar prompts visuales (`images.main.prompt.current`) contra plantilla estructurada v1 y coherencia minima, generar `NN.review.json|md` y sincronizar `NN.decisions.json` para correccion manual.
---

# Auditoria de Prompts

Ejecutar esta skill solo cuando el texto ya no tenga bloqueos (`text_reviewed`).

## Flujo

1. Confirmar `book_rel_path` y `story_id`.
2. Ejecutar `run_prompt_audit`.
3. Revisar hallazgos en `NN.review.json` y `NN.review.md`.
4. Completar decisiones en `NN.decisions.json`.

## Plantilla estructurada v1 objetivo

- `SUJETO:`
- `ESCENA:`
- `ESTILO:`
- `COMPOSICION:`
- `ILUMINACION_COLOR:`
- `CONTINUIDAD:`
- `RESTRICCIONES:`

## Comando recomendado

```powershell
@'
from app.editorial_osmosis import run_prompt_audit

result = run_prompt_audit(
    book_rel_path="cosmere/nacidos-de-la-bruma-era-1/el-imperio-final",
    story_id="01",
)
print(result["review_json_rel"])
print(result["decisions_json_rel"])
print("status", result["status"], "findings", result["findings"])
'@ | python -
```
