# Guia de orquestacion editorial

Documento reducido. La operacion oficial y vigente del flujo 3 IAs vive en `AGENTS.md`.

Resumen:

1. NotebookLM entrega `NN.json` (+ `meta.json` opcional) en `_inbox`.
2. Codex ejecuta `ingesta-cuentos` para validar/importar y emitir deltas.
3. ChatGPT Project genera imagenes a partir de prompts/anchors.

Para reglas, contratos y mensajes base, usar siempre `AGENTS.md`.
