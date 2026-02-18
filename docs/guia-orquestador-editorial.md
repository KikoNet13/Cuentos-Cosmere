# Guia de orquestacion editorial

Documento reducido. La operacion oficial y vigente del flujo 3 IAs vive en `AGENTS.md`.

Resumen:

1. Codex usa `notebooklm-comunicacion` en 4 fases:
   - plan de coleccion,
   - `meta.json` (anclas + reglas),
   - prompts de cuentos por partes (`NN_a/_b`, fallback `a1/a2/b1/b2`),
   - deltas de correccion por archivo.
2. NotebookLM entrega JSON en `_inbox` (`NN.json` o partes) y `meta.json` recomendado para flujo listo de imagen.
3. Codex ejecuta `ingesta-cuentos` para fusionar en memoria, validar, enriquecer `reference_ids` y luego importar.
4. ChatGPT Project genera imagenes a partir de prompts + anchors (`reference_ids` basados en `meta.anchors[].image_filenames`).

Para reglas, contratos y mensajes base, usar siempre `AGENTS.md`.
