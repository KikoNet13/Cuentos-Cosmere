# TAREA-026 - Automatizacion de anclas en flujo 2 skills

- Fecha: 18/02/26 15:03
- Estado: cerrada
- Versión objetivo: 2.3.0

## Resumen

Se cierra la automatizacion del tramo NotebookLM -> Ingesta para dejar lotes listos para generación de imagen:

1. `notebooklm-comunicacion` pasa a operar en 4 fases (plan, meta/anclas, partes, deltas).
2. `ingesta-cuentos` incorpora enriquecimiento preimport de `reference_ids` cuando faltan.
3. Se formaliza estrategia hibrida de referencias:
   - NotebookLM propone refs cuando puede.
   - `ingesta-cuentos` autocompleta faltantes usando `meta.anchors[].image_filenames`.

## Alcance implementado

1. Skill `notebooklm-comunicacion` actualizada:
   - flujo oficial en 4 fases;
   - plantilla de prompt para `meta.json` con `collection`, `anchors`, `style_rules`, `continuity_rules`, `updated_at`;
   - convencion de IDs por categoria (`style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`);
   - plantillas `NN_a/NN_b` pidiendo `reference_ids` basados en `meta`;
   - deltas especializados para JSON truncado/invalido, rango de páginas y refs faltantes.
2. `notebooklm-comunicacion/agents/openai.yaml` actualizado:
   - descripcion y prompt por defecto alineados a meta/anclas + refs.
3. Skill `ingesta-cuentos` actualizada:
   - etapa de enriquecimiento preimport de referencias;
   - precedencia: conservar refs existentes y autocompletar faltantes;
   - fallback de estilo + deteccion semantica;
   - warnings de cobertura de refs;
   - tolerancia declarada a UTF-8 y UTF-8 BOM en `_inbox`.
4. Contrato de referencia (`ingesta-cuentos/references/contracts.md`) actualizado:
   - convencion operativa de `reference_ids` contra `meta.anchors[].image_filenames[]`;
   - reglas de enriquecimiento automático;
   - warnings nuevos (`refs.autofilled`, `refs.style_only_fallback`, `refs.anchor_missing`);
   - compatibilidad UTF-8/UTF-8 BOM.
5. Documentacion orquestadora actualizada:
   - `AGENTS.md`;
   - `docs/guia-orquestador-editorial.md`.

## Validaciones ejecutadas

1. Revisión de consistencia de skills y contrato:
   - `Get-Content -Raw .codex/skills/notebooklm-comunicacion/SKILL.md`
   - `Get-Content -Raw .codex/skills/ingesta-cuentos/SKILL.md`
   - `Get-Content -Raw .codex/skills/ingesta-cuentos/references/contracts.md`
2. Verificacion de orquestacion/documentacion:
   - `Get-Content -Raw AGENTS.md`
   - `Get-Content -Raw docs/guia-orquestador-editorial.md`
   - `Get-Content -Raw docs/tasks/INDICE.md`
   - `Get-Content -Raw CHANGELOG.md`
3. Verificacion de estado de lote real en `_inbox` para robustez de entrada:
   - deteccion de JSON con BOM y caso truncado (`07_b`) en `Los juegos del hambre`.

## Archivos principales tocados

- `.codex/skills/notebooklm-comunicacion/SKILL.md`
- `.codex/skills/notebooklm-comunicacion/agents/openai.yaml`
- `.codex/skills/ingesta-cuentos/SKILL.md`
- `.codex/skills/ingesta-cuentos/references/contracts.md`
- `AGENTS.md`
- `docs/guia-orquestador-editorial.md`
- `docs/tasks/TAREA-026-automatizacion-anclas-flujo-2-skills.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
