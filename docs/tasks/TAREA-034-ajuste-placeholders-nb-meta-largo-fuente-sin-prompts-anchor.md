# TAREA-034 - Ajuste placeholders NB: meta largo + fuente sin prompts de anchors

- Fecha: 18/02/26 22:25
- Estado: cerrada
- Versión objetivo: 2.7.4

## Resumen

Se corrige el parche de orquestacion para NotebookLM en dos puntos:

1. `meta_prompts.json` ahora exige prompts largos estructurados tambien para `anchors[].prompt`.
2. `FUENTE_NB_los_juegos_textos_y_anchors.md` elimina los prompts de anchors y conserva solo `id`, `name`, `image_filenames` + textos narrativos.

## Alcance implementado

1. Actualización de `meta_prompts.json`:
   - mantiene salida JSON estricta;
   - mantiene IDs canónicos obligatorios;
   - agrega regla explicita de 8 bloques para cada `anchors[].prompt`;
   - agrega rango de longitud 700-1500 para prompts de anchors.
2. Limpieza de fuente NB:
   - se eliminan lineas `- prompt:` en la sección `Anchors Canonicos (meta)`;
   - no se toca el contenido narrativo por cuento/pagina.

## Validaciones ejecutadas

1. Verificacion de fuente:
   - `rg -n "^- prompt:" library/_inbox/Los juegos del hambre/FUENTE_NB_los_juegos_textos_y_anchors.md` sin resultados.
2. Verificacion de placeholder meta:
   - `meta_prompts.json` contiene rango y estructura de 8 bloques para `anchors[].prompt`.
3. Diff acotado:
   - cambios solo en `meta_prompts.json`, `FUENTE_NB...`, y documentacion de tarea/indice/changelog.

## Archivos principales tocados

- `library/_inbox/Los juegos del hambre/meta_prompts.json`
- `library/_inbox/Los juegos del hambre/FUENTE_NB_los_juegos_textos_y_anchors.md`
- `docs/tasks/TAREA-034-ajuste-placeholders-nb-meta-largo-fuente-sin-prompts-anchor.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
