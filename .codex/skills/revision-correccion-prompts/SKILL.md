---
name: revision-correccion-prompts
description: Aplicar decisiones aceptadas sobre prompts (`images.main.prompt.current`) usando `NN.decisions.json`, recalcular bloqueos y actualizar estado del cuento a `prompt_reviewed` o `prompt_blocked`.
---

# Correccion de Prompts

Ejecutar esta skill despues de revisar decisiones de prompts.

## Flujo

1. Validar decisiones en `NN.decisions.json`.
2. Ejecutar `run_prompt_correction`.
3. Confirmar prompts aplicados y estado resultante.
4. Si queda sin bloqueos, avanzar a cierre (`ready` en orquestadora).

## Comando recomendado

```powershell
@'
from app.editorial_osmosis import run_prompt_correction

result = run_prompt_correction(
    book_rel_path="cosmere/nacidos-de-la-bruma-era-1/el-imperio-final",
    story_id="01",
)
print(result["review_json_rel"])
print("status", result["status"], "metrics", result["metrics"])
'@ | python -
```
