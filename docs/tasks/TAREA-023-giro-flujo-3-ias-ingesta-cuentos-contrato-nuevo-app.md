# TAREA-023 - Giro a flujo 3 IAs con `ingesta-cuentos` + contrato nuevo JSON + app alineada

- Fecha: 17/02/26 18:03
- Estado: cerrada
- Version objetivo: 2.0.0

## Resumen

Se reorienta el repositorio al flujo 3 IAs:

1. NotebookLM entrega `NN.json` (+ `meta.json` opcional) en `_inbox`.
2. Codex valida/importa con la skill `ingesta-cuentos` y emite mensajes accionables.
3. ChatGPT Project genera imagenes usando prompts/anchors del contrato final.

La app y la documentacion quedan migradas al formato nuevo, sin dependencia operativa del esquema legacy.

## Alcance implementado

1. Skill nueva `.codex/skills/ingesta-cuentos/`:
   - conversacional;
   - sin scripts;
   - contrato de validacion/importacion de `NN.json` y `meta.json`;
   - plantillas de mensajes para NotebookLM y ChatGPT Project.
2. Retiro de la skill anterior:
   - eliminado `.codex/skills/adaptacion-ingesta-inicial/`.
3. Refactor de runtime de app al contrato nuevo:
   - `app/story_store.py` reescrito:
     - `text` string por pagina;
     - `prompt` string por slot;
     - `cover` como slot completo;
     - almacenamiento de imagenes en `<node>/images/`;
     - nombre opaco `<uuid>_<slug>.<ext>`;
     - actualizacion automatica de `images/index.json`;
     - soporte de `meta.json` por nodo, jerarquia y anclas.
   - UI/editor adaptado:
     - edicion simple de texto/prompt;
     - `reference_ids[]` visibles con warning de faltantes;
     - portada editable como slot completo;
     - panel de anclas jerarquicas con alta/edicion, alternativas y activacion.
4. Documentacion actualizada:
   - `AGENTS.md` (flujo 3 IAs y contrato nuevo);
   - `README.md`, `app/README.md`;
   - `docs/guia-orquestador-editorial.md` reducido y alineado a AGENTS.
5. Biblioteca:
   - reseteo solicitado: limpieza de `library/` excepto `_inbox`.

## Validaciones ejecutadas

1. `python -m compileall app`
2. Verificacion de referencias legacy en `app/`:
   - sin dependencias a `text.original/current` ni `prompt.original/current`.
3. Verificacion de estructura de skills:
   - existe `ingesta-cuentos`;
   - no existe `adaptacion-ingesta-inicial` en archivos versionados.

## Notas de contrato

1. `NN.json` nuevo:
   - sin `schema_version`, `story_title`, `source_refs`, `ingest_meta`.
2. `meta.json`:
   - soportado en libro + ancestros + global.
3. Sidecars legacy de adaptacion:
   - fuera de contrato en esta etapa.

## Archivos principales tocados

- `.codex/skills/ingesta-cuentos/SKILL.md`
- `.codex/skills/ingesta-cuentos/agents/openai.yaml`
- `.codex/skills/ingesta-cuentos/references/contracts.md`
- `app/story_store.py`
- `app/catalog_provider.py`
- `app/web/routes_story_editor.py`
- `app/web/viewmodels.py`
- `app/templates/story/editor/page.html`
- `app/templates/story/read/_shell.html`
- `app/templates/story/read/_advanced_panel.html`
- `app/templates/components/story/editor_slot_card.html`
- `AGENTS.md`
- `README.md`
- `app/README.md`
- `docs/guia-orquestador-editorial.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
