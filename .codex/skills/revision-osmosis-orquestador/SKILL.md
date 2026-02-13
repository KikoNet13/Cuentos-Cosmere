---
name: revision-osmosis-orquestador
description: Orquestar pipeline editorial completo por libro (ingesta, auditoria/correccion de texto, auditoria/correccion de prompts) con sidecars `_reviews`, bloqueo por `critical|major` y detencion del libro en el primer cuento bloqueado.
---

# Orquestador Osmosis

Ejecutar esta skill cuando se quiera procesar un libro completo en un solo flujo.

## Fases

1. Descubrimiento de fuentes (`_ignore` excluido, prioridad raiz en duplicados).
2. Ingesta a `NN.json`.
3. Auditoria + correccion de texto por cuento.
4. Gate:
   - si hay `critical_open > 0` o `major_open > 0`, marcar `text_blocked` y detener libro.
5. Auditoria + correccion de prompts por cuento.
6. Gate:
   - si hay `critical_open > 0` o `major_open > 0`, marcar `prompt_blocked` y detener libro.
7. Cierre:
   - si pasa todo, marcar cuento en `ready`.

## Comando recomendado

```powershell
@'
from app.editorial_osmosis import run_osmosis_pipeline

result = run_osmosis_pipeline(
    inbox_book_title="El imperio final",
    book_rel_path="cosmere/nacidos-de-la-bruma-era-1/el-imperio-final",
)
print(result["phase"])
print(result["pipeline_state_rel"])
print("totals", result["totals"])
if result.get("blocked_story"):
    print("blocked_story", result["blocked_story"])
'@ | python -
```

## Artefactos

- `library/<book_rel_path>/_reviews/pipeline_state.json`
- `library/<book_rel_path>/_reviews/NN.review.json`
- `library/<book_rel_path>/_reviews/NN.review.md`
- `library/<book_rel_path>/_reviews/NN.decisions.json`
