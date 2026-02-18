# Guia de orquestacion editorial

Documento reducido. La operacion oficial y vigente del flujo 3 IAs vive en `AGENTS.md`.

Resumen:

1. Codex puede usar `notebooklm-comunicacion` para preparar prompts por partes (`NN_a/_b`, fallback `a1/a2/b1/b2`).
2. NotebookLM entrega JSON en `_inbox` (cuento completo o por partes) + `meta.json` opcional.
3. Codex ejecuta `ingesta-cuentos` para fusionar en memoria, validar/importar y emitir deltas.
4. ChatGPT Project genera imagenes a partir de prompts/anchors.

Para reglas, contratos y mensajes base, usar siempre `AGENTS.md`.
