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
4. `ingesta-cuentos` regenera `library/<book_rel_path>/chatgpt_project_setup.md` (y permite refresh manual sin reimportar).
5. ChatGPT Project genera imagenes a partir de prompts + anchors (`reference_ids` basados en `meta.anchors[].image_filenames`).
6. Operacion recomendada en UI para imagen:
   - abrir `/_flow/image`,
   - la app muestra solo el primer pendiente global,
   - copiar prompt + refs, generar en ChatGPT Project,
   - usar "Pegar y guardar";
   - recarga automatica al siguiente pendiente.
7. Orden de prioridad visual del flujo guiado:
   - primero todas las anclas pendientes,
   - despues portada/main/secondary de cuentos.

Para reglas, contratos y mensajes base, usar siempre `AGENTS.md`.
