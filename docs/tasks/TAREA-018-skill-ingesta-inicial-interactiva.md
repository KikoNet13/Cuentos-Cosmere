# TAREA-018-skill-ingesta-inicial-interactiva

## Metadatos

- ID de tarea: `TAREA-018-skill-ingesta-inicial-interactiva`
- Fecha: 16/02/26 12:49
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Implementar una skill de ingesta inicial interactiva para convertir propuestas `NN.md` + `NN.pdf` en:

- `library/<book_rel_path>/NN.json`
- `library/<book_rel_path>/_reviews/adaptation_context.json`
- `library/<book_rel_path>/_reviews/NN.issues.json`

con preguntas de usuario para `target_age`, `book_rel_path` y glosario ambiguo.

## Contexto

El runtime de `app/` ya usa `NN.json` como fuente de verdad, pero faltaba una skill de ingesta inicial con salida estructurada y contrato de sidecars para etapa "en revision".

## Plan

1. Crear skill versionada para ingesta inicial con script CLI no bloqueante.
2. Extender `app/story_store.py` para soportar metadatos top-level nuevos y estados `in_review|definitive`.
3. Actualizar documentacion operativa y trazabilidad (tarea, indice, changelog).
4. Validar comandos finitos y flujo interactivo (`awaiting_user` -> `completed`).

## Decisiones

- La skill se versiona en `.codex/skills/adaptacion-ingesta-inicial/`.
- El script no llama APIs LLM: toda interaccion semantica se resuelve en chat Codex.
- El script procesa batch del libro completo y excluye `_ignore`.
- Si falta `NN.pdf`, se registra hallazgo `critical` sin bloquear el libro completo.
- `NN.json` se crea con estado `in_review` y metadatos extra (`story_title`, `cover`, `source_refs`, `ingest_meta`).

## Cambios aplicados

- Skill nueva:
  - `.codex/skills/adaptacion-ingesta-inicial/SKILL.md`
  - `.codex/skills/adaptacion-ingesta-inicial/agents/openai.yaml`
  - `.codex/skills/adaptacion-ingesta-inicial/references/contracts.md`
  - `.codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py`
- Runtime:
  - `app/story_store.py`
- Documentacion:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/tasks/TAREA-018-skill-ingesta-inicial-interactiva.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

1. `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py --help`
2. `python C:/Users/Kiko/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/adaptacion-ingesta-inicial`
   - Resultado: no ejecutable por dependencia faltante `yaml` en ese validador global.
3. `python -c "import re; from pathlib import Path; t=Path('.codex/skills/adaptacion-ingesta-inicial/SKILL.md').read_text(encoding='utf-8'); m=re.match(r'^---\\n(.*?)\\n---\\n', t, flags=re.S); assert m and 'name:' in m.group(1) and 'description:' in m.group(1); print('manual-skill-frontmatter-ok')"`
4. `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "El imperio final" --dry-run`
   - Resultado: `phase=awaiting_user`, con preguntas de `book_rel_path`, `target_age` y glosario ambiguo.
5. `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "El imperio final" --book-rel-path "cosmere/tmp-ingesta-inicial/el-imperio-final" --answers-json tmp/ingesta_answers.json --dry-run`
   - Resultado: `phase=completed`.
6. `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "El imperio final" --book-rel-path "cosmere/tmp-ingesta-inicial/el-imperio-final" --answers-json tmp/ingesta_answers.json`
   - Resultado: `phase=completed` con `written_outputs` para `01..03.json`, `01..03.issues.json` y `adaptation_context.json`.
7. `python -c "from app.story_store import load_story, save_page_edits; s='cosmere/tmp-ingesta-inicial/el-imperio-final/01'; p=load_story(s); print('before', all(k in p for k in ('story_title','cover','source_refs','ingest_meta'))); pg=p['pages'][0]['page_number']; save_page_edits(story_rel_path=s, page_number=pg, text_current=p['pages'][0]['text']['current'], main_prompt_current=p['pages'][0]['images']['main']['prompt']['current'], secondary_prompt_current=''); p2=load_story(s); print('after', all(k in p2 for k in ('story_title','cover','source_refs','ingest_meta')))"`.
   - Resultado: `before True` y `after True`.

## Riesgos

- Deteccion semantica profunda depende de la etapa conversacional de la skill; el script se limita a heuristicas deterministas.
- Si el parser PDF local no esta disponible, los hallazgos dependen de `NN.md` y se marca issue `major`.

## Seguimiento

1. Ajustar UI para exponer `cover` y estados `in_review|definitive`.

## Commit asociado

- Mensaje de commit: `Tarea 018: skill de ingesta inicial interactiva`
- Hash de commit: pendiente
