# TAREA-040 - Refs semánticas y naming sin UUID

- Fecha: 19/02/26 09:05
- Estado: cerrada
- Responsable: Codex
- ADR relacionadas: `0008`

## Resumen
Se implementa la limpieza semántica de `reference_ids` en `library/los_juegos_del_hambre/01..11.json`, la migración operativa a naming legible sin UUID y la actualización de guías del Project para operar con pack global de 27 anclas.

## Alcance aplicado
1. Datos de saga (`library/los_juegos_del_hambre`):
- Backup no destructivo en `library/_backups/los_juegos_del_hambre-refs-naming-20260219T084140Z/`.
- Migración de anclas a `images/anchors/<slug>.png`.
- Reescritura de `meta.json` e `images/index.json` para naming legible.
- Limpieza de `reference_ids` en `01..11.json` con política semántica y cap de 6.

2. Runtime (`app/story_store.py`):
- Nuevo naming sin UUID para uploads nuevos.
- Detección de colisión por slug con error explícito.
- Soporte de escritura en subcarpetas de `images/`.
- Resolución de referencias con rutas relativas (`anchors/...`) + fallback legacy (`anchor_*.png`, `char_*_base`).

3. Instrucciones operativas:
- `chatgpt_projects_setup/Los juegos del hambre - Imagenes editoriales (16p).md`.
- `chatgpt_projects_setup/PASOS_OPERATIVOS.md`.
- Nuevo manifiesto: `chatgpt_projects_setup/Los juegos del hambre - Adjuntos globales (27 anclas).md`.

4. Pipeline global/documentación:
- `AGENTS.md`.
- `.codex/skills/ingesta-cuentos/SKILL.md`.
- `.codex/skills/ingesta-cuentos/references/contracts.md`.
- `.codex/skills/ingesta-cuentos/references/chatgpt_project_setup_template.md`.

## Cambios técnicos clave
1. Convención de `reference_ids`:
- Canónica por ruta relativa en `images/`.
- Formato preferente de anclas: `anchors/<slug>.png`.

2. Convención de naming de assets nuevos:
- Anclas: `images/anchors/<slug>.<ext>`.
- Slots: `images/<NN>/<NN>_<MM>_<slot>-<slug>.<ext>`.

3. Reglas de refs por slot:
- Máximo 6 referencias.
- Eliminación de `style_linea_editorial` y `style_paleta_rebelion` de slots (pack global del Project).
- Resolución solo contra referencias existentes.

## Validaciones ejecutadas
1. Integridad JSON:
- `JSON_OK=13` (meta + index + 01..11).

2. Cobertura y reglas de referencias:
- `ANCHORS_META=27`
- `PARSE_OK=11`
- `SLOT_COUNT=187`
- `MAX6_OK=True`
- `STYLE_REFS_IN_SLOTS=0`
- `MISSING_REFS=0`

3. Runtime de resolución (smoke tests):
- `resolve_reference_assets` resuelve correctamente:
  - `anchors/char-katniss.png`
  - `anchor_char_katniss.png`
  - `char_katniss_base`

4. Naming/collisions:
- `_build_slot_image_name` y `_build_cover_image_name` generan formato legible esperado.
- Colisión detectada correctamente para slug existente (`anchors/char-katniss.png`).

## Resultado
TAREA-040 completada con migración de naming sin UUID, refs semánticas limpias en `01..11`, compatibilidad runtime legacy y guías operativas actualizadas para uso de 27 anclas globales en ChatGPT Project.
