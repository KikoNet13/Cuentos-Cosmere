---
name: revision-correccion-texto
description: Aplicar correcciones manuales asistidas sobre `text.current` usando decisiones aceptadas en `NN.decisions.json`, recalcular hallazgos abiertos y actualizar estado del cuento a `text_reviewed` o `text_blocked`.
---

# Correccion de Texto

Ejecutar esta skill despues de editar decisiones en `NN.decisions.json`.

## Flujo

1. Verificar que cada finding tenga `decision` y `selected_option` cuando corresponda.
2. Ejecutar `run_text_correction`.
3. Confirmar cambios en `text.current`.
4. Revisar gate:
   - `blocked` si quedan `critical_open` o `major_open`.
   - `approved` si no quedan.

## Comando recomendado

```powershell
@'
from app.editorial_osmosis import run_text_correction

result = run_text_correction(
    book_rel_path="cosmere/nacidos-de-la-bruma-era-1/el-imperio-final",
    story_id="01",
)
print(result["review_json_rel"])
print("status", result["status"], "metrics", result["metrics"])
'@ | python -
```
