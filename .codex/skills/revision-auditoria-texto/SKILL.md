---
name: revision-auditoria-texto
description: Auditar `text.current` de un cuento `NN.json`, generar hallazgos con severidad y propuestas A/B/C en `NN.review.json` y `NN.review.md`, y sincronizar `NN.decisions.json`.
---

# Auditoria de Texto

Ejecutar esta skill para detectar incoherencias y deuda editorial del texto.

## Flujo

1. Confirmar `book_rel_path` y `story_id`.
2. Ejecutar `run_text_audit`.
3. Revisar `NN.review.json` y `NN.review.md`.
4. Completar decisiones en `NN.decisions.json`.

## Comando recomendado

```powershell
@'
from app.editorial_osmosis import run_text_audit

result = run_text_audit(
    book_rel_path="cosmere/nacidos-de-la-bruma-era-1/el-imperio-final",
    story_id="01",
)
print(result["review_json_rel"])
print(result["decisions_json_rel"])
print("status", result["status"], "findings", result["findings"])
'@ | python -
```

## Contrato de salida

- `library/<book_rel_path>/_reviews/NN.review.json`
- `library/<book_rel_path>/_reviews/NN.review.md`
- `library/<book_rel_path>/_reviews/NN.decisions.json`
