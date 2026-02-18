# TAREA-027 - Modo rapido de imagen + dossier ChatGPT Project por saga

- Fecha: 18/02/26 16:35
- Estado: cerrada
- Versión objetivo: 2.4.0

## Resumen

Se implementa el tramo final del flujo de imagen para reducir friccion operativa en editor y dejar un dossier reutilizable por saga:

1. La webapp incorpora barra "Modo rapido" en editor de slots y portada.
2. Se habilita acción de un clic para `Pegar y guardar alternativa` desde portapapeles.
3. La skill `ingesta-cuentos` queda documentada para generar/refrescar `chatgpt_project_setup.md`.

## Alcance implementado

1. UI de editor (página y portada):
   - barra compacta con:
     - copiar prompt,
     - copiar referencias individuales del slot,
     - pegar y guardar alternativa en un clic.
   - mantenimiento del flujo manual existente (no se elimina fallback).
2. JS de portapapeles:
   - nueva funcion `pasteImageAndSubmit(inputId, feedbackId, formId)`;
   - `pasteImageToHidden(...)` devuelve estado booleano y mensajes claros;
   - no envia formulario cuando falta imagen o falla lectura del portapapeles.
3. Estilos:
   - nueva clase `quick-actions-bar` en `app/static/css/pages.css`.
4. Skill `ingesta-cuentos`:
   - objetivo y flujo actualizados para regenerar `library/<book_rel_path>/chatgpt_project_setup.md` tras ingesta válida;
   - modo `refresh manual` del dossier sin reimportar cuentos;
   - plantilla documental del dossier incluida en la skill.
5. Contrato de referencia:
   - `chatgpt_project_setup.md` documentado como artefacto operativo (no canónico).
6. Orquestacion/documentacion:
   - `AGENTS.md`, `README.md` y `docs/guia-orquestador-editorial.md` alineados al nuevo flujo.

## Validaciones ejecutadas

1. Verificacion de templates/JS/CSS:
   - `Get-Content -Raw app/templates/components/story/editor_slot_card.html`
   - `Get-Content -Raw app/templates/story/editor/cover.html`
   - `Get-Content -Raw app/static/js/clipboard.js`
   - `Get-Content -Raw app/static/css/pages.css`
2. Verificacion de skill y contrato:
   - `Get-Content -Raw .codex/skills/ingesta-cuentos/SKILL.md`
   - `Get-Content -Raw .codex/skills/ingesta-cuentos/references/contracts.md`
   - `Get-Content -Raw .codex/skills/ingesta-cuentos/agents/openai.yaml`
3. Verificacion de sintaxis Python (smoke):
   - `python -m compileall app`
4. Verificacion de estado y diff:
   - `git status --short`
   - `git diff -- <archivos tocados>`

## Archivos principales tocados

- `app/templates/components/story/editor_slot_card.html`
- `app/templates/story/editor/cover.html`
- `app/static/js/clipboard.js`
- `app/static/css/pages.css`
- `.codex/skills/ingesta-cuentos/SKILL.md`
- `.codex/skills/ingesta-cuentos/references/contracts.md`
- `.codex/skills/ingesta-cuentos/references/chatgpt_project_setup_template.md`
- `.codex/skills/ingesta-cuentos/agents/openai.yaml`
- `AGENTS.md`
- `README.md`
- `docs/guia-orquestador-editorial.md`
- `docs/tasks/TAREA-027-modo-rapido-imagen-dossier-project-saga.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
