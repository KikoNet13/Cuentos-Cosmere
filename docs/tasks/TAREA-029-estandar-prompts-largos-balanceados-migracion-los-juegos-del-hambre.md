# TAREA-029 - Estandar de prompts largos balanceados + migracion Los juegos del hambre

- Fecha: 18/02/26 21:45
- Estado: cerrada
- Version objetivo: 2.6.0

## Resumen

Se implementa un estandar global de prompts largos para imagen en el flujo NotebookLM -> Ingesta -> ChatGPT Project y se migra `library/los_juegos_del_hambre/01..11.json` al formato tipo Hansel con perfil balanceado.

## Alcance implementado

1. Skill `notebooklm-comunicacion` actualizada:
   - nuevo estandar obligatorio de 8 bloques para `cover.prompt` y `pages[].images.main.prompt`;
   - longitudes del perfil balanceado:
     - portada: `900-1700`;
     - pagina main: `700-1500`;
   - idioma canonico: espanol estructurado;
   - nueva plantilla de reentrega `prompts-only` para cuentos existentes;
   - nuevos codigos delta de prompts:
     - `prompts.too_short`
     - `prompts.missing_sections`
     - `prompts.language_mismatch`
     - `prompts.range_incomplete`
2. Agent metadata de la skill alineada al nuevo estandar:
   - `notebooklm-comunicacion/agents/openai.yaml` actualizado.
3. Documentacion operativa de Project alineada:
   - gate obligatorio para validar los 8 bloques antes de generar;
   - regla explicita: si prompt incompleto/corto, no generar y pedir delta a NotebookLM.
4. Migracion de saga `Los juegos del hambre`:
   - backup previo no destructivo en:
     - `library/_backups/los_juegos_del_hambre-prompts-20260218T204333Z/`
   - reescritura de prompts en `01..11.json`:
     - portada y pages.main en formato largo balanceado;
     - preservando `text`, `reference_ids`, `active_id`, `alternatives`, `page_number`.
   - actualizacion de `updated_at` en cada cuento migrado.
5. Dossier de saga regenerado:
   - nuevo `library/los_juegos_del_hambre/chatgpt_project_setup.md`.

## Validaciones ejecutadas

1. Skill docs (sin legado de prompts cortos):
   - `rg -n "1-2 frases|prompt: 1-2" .codex/skills/notebooklm-comunicacion -S`
   - resultado: `NO_MATCHES`.
2. Validacion estructural de prompts migrados:
   - script Python local:
     - verifica 8 encabezados obligatorios en cover/main;
     - verifica rangos de longitud por slot;
   - resultado: `PROMPT_VALIDATION_OK`.
3. Integridad de migracion (solo prompts + updated_at):
   - comparacion estructurada contra backup;
   - resultado: `INTEGRITY_OK`.
4. Contrato de cuentos 01..11:
   - parse JSON + secuencia de paginas `1..16` por cuento;
   - resultado: `SEQ_OK`.
5. Validacion operativa rapida de flujo guiado:
   - `GET /_flow/image` con `Flask test_client`;
   - resultado: `flow_status=200`;
   - snapshot de pendientes en saga:
     - `cover::los_juegos_del_hambre/01`
     - `slot::los_juegos_del_hambre/01::1::main`

## Archivos principales tocados

- `.codex/skills/notebooklm-comunicacion/SKILL.md`
- `.codex/skills/notebooklm-comunicacion/agents/openai.yaml`
- `.codex/skills/ingesta-cuentos/references/chatgpt_project_setup_template.md`
- `chatgpt_projects_setup/PASOS_OPERATIVOS.md`
- `chatgpt_projects_setup/Los juegos del hambre - Imagenes editoriales (16p).md`
- `library/los_juegos_del_hambre/01.json`
- `library/los_juegos_del_hambre/02.json`
- `library/los_juegos_del_hambre/03.json`
- `library/los_juegos_del_hambre/04.json`
- `library/los_juegos_del_hambre/05.json`
- `library/los_juegos_del_hambre/06.json`
- `library/los_juegos_del_hambre/07.json`
- `library/los_juegos_del_hambre/08.json`
- `library/los_juegos_del_hambre/09.json`
- `library/los_juegos_del_hambre/10.json`
- `library/los_juegos_del_hambre/11.json`
- `library/los_juegos_del_hambre/chatgpt_project_setup.md`
- `library/_backups/los_juegos_del_hambre-prompts-20260218T204333Z/*.json`
- `docs/tasks/TAREA-029-estandar-prompts-largos-balanceados-migracion-los-juegos-del-hambre.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
