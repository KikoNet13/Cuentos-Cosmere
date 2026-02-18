# TAREA-029 - Style Prompt Maestro en setup ChatGPT Project (Los juegos del hambre)

## Metadatos

- ID de tarea: `TAREA-029-style-prompt-maestro-chatgpt-project`
- Fecha: 18/02/26 21:50
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0008`

## Objetivo

Incorporar en las instrucciones de ChatGPT Project un bloque explicito y reutilizable de estilo canonico para reducir deriva visual, junto con reglas operativas de composicion por intencion del slot.

## Contexto

Los documentos operativos tenian reglas de continuidad generales, pero no fijaban un `Style Prompt Maestro` literal ni una politica explicita de uso de `full-bleed` vs `spot art` por intencion del slot.

## Plan

1. Actualizar setup de saga actual con bloque de estilo canonico y modificadores de composicion.
2. Actualizar guia operativa generica para forzar verificacion de estilo y decision de composicion por slot.
3. Actualizar plantilla oficial de dossier en `ingesta-cuentos` con placeholders genericos de style prompt.
4. Sincronizar ejemplo B2 de `SKILL.md` con la plantilla oficial.
5. Registrar trazabilidad en tarea, indice y changelog.
6. Cerrar con commit unico y push en `main`.

## Decisiones

- El prompt de estilo en ingles se conserva literal como canon.
- Se agrega resumen tecnico breve en espanol como apoyo operativo.
- La composicion (`full-bleed` / `spot art`) se aplica solo cuando el slot/prompt lo pide de forma explicita.
- No se tocaron `library/los_juegos_del_hambre/*.json` ni `library/los_juegos_del_hambre/meta.json`.
- No se crea ni modifica `library/los_juegos_del_hambre/chatgpt_project_setup.md` en esta tarea.

## Cambios aplicados

- `chatgpt_projects_setup/Los juegos del hambre - Imagenes editoriales (16p).md`
  - Seccion `STYLE PROMPT MAESTRO (CANONICO)` (EN literal + resumen ES).
  - Seccion `MODIFICADORES DE COMPOSICION`.
  - Regla explicita de uso por slot/prompt.
- `chatgpt_projects_setup/PASOS_OPERATIVOS.md`
  - Verificacion obligatoria del style prompt en preparacion.
  - Paso de decision de composicion por intencion del slot.
  - Checklist QA con invariantes tecnicos de estilo.
- `.codex/skills/ingesta-cuentos/references/chatgpt_project_setup_template.md`
  - Bloque generico `Style Prompt Maestro de la saga` con placeholders.
  - Politica de composicion por intencion del slot.
- `.codex/skills/ingesta-cuentos/SKILL.md`
  - Bloque B2 sincronizado con plantilla oficial.
- `docs/tasks/INDICE.md`
  - Registro de TAREA-029 alineado a este alcance.
- `CHANGELOG.md`
  - Entrada breve de cambios enlazada a esta tarea.

## Validacion ejecutada

1. `rg -n "STYLE PROMPT MAESTRO|MODIFICADORES DE COMPOSICION|full-bleed|spot art" "chatgpt_projects_setup/Los juegos del hambre - Imagenes editoriales (16p).md" "chatgpt_projects_setup/PASOS_OPERATIVOS.md" ".codex/skills/ingesta-cuentos/references/chatgpt_project_setup_template.md" ".codex/skills/ingesta-cuentos/SKILL.md" -S`
2. `git diff -- "chatgpt_projects_setup/Los juegos del hambre - Imagenes editoriales (16p).md" "chatgpt_projects_setup/PASOS_OPERATIVOS.md" ".codex/skills/ingesta-cuentos/references/chatgpt_project_setup_template.md" ".codex/skills/ingesta-cuentos/SKILL.md" "docs/tasks/TAREA-029-style-prompt-maestro-chatgpt-project.md" "docs/tasks/INDICE.md" "CHANGELOG.md"`

## Riesgos

- Si se regenera un dossier sin completar placeholders del style prompt, puede quedar setup incompleto para una saga nueva.

## Seguimiento

1. En la proxima regeneracion de dossier por saga, completar los placeholders del style prompt con canon editorial aprobado.

## Commit asociado

- Mensaje de commit: `Tarea 029: incorporar style prompt maestro en setup ChatGPT Project`
- Hash de commit: `pendiente`
