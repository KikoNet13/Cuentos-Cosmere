---
name: revision-ingesta-json
description: Ejecutar la fase de ingesta editorial desde `library/_inbox/<libro>` hacia `library/<book_rel_path>/NN.json`, ignorando carpetas `_ignore`, priorizando duplicados en raiz y registrando inventario en `_reviews/pipeline_state.json`.
---

# Ingesta JSON

Ejecutar esta skill para crear o actualizar cuentos `NN.json` desde propuestas `NN.md`.

## Flujo

1. Confirmar `inbox_book_title` y `book_rel_path`.
2. Ejecutar la ingesta con `run_ingesta_json`.
3. Revisar inventario generado en `_reviews/pipeline_state.json`.
4. Confirmar seleccionados, ignorados y no-touch.

## Comando recomendado

```powershell
@'
from app.editorial_osmosis import run_ingesta_json

result = run_ingesta_json(
    inbox_book_title="El imperio final",
    book_rel_path="cosmere/nacidos-de-la-bruma-era-1/el-imperio-final",
)
print(result["pipeline_state_rel"])
print("selected", result["totals"]["selected"], "ingested", result["totals"]["ingested"])
'@ | python -
```

## Reglas

- Ignorar carpetas llamadas exactamente `_ignore`.
- Priorizar archivo en raiz cuando haya duplicado `NN.md`.
- No tocar `NN.json` existente cuando la fuente viva solo en `_ignore`.
