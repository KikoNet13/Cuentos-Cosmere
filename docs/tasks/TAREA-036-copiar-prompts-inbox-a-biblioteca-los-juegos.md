# TAREA-036 - Copiar prompts de `_inbox` a biblioteca de `los_juegos_del_hambre`

- Fecha: 19/02/26 00:32
- Estado: cerrada
- Versión objetivo: 2.7.6

## Resumen

Se copiaron los prompts ya rellenados en `library/_inbox/Los juegos del hambre/*_prompts.json` a sus cuentos definitivos en `library/los_juegos_del_hambre/NN.json`.

## Alcance aplicado

1. Cuentos afectados: `01.json` a `11.json`.
2. Campos actualizados por cuento:
   - `cover.prompt` desde `cover_prompt`.
   - `pages[].images.main.prompt` desde `page_prompts[].main_prompt`.
   - `updated_at` del cuento desde `updated_at` del `_prompts.json`.
3. Sin cambios en:
   - `text`,
   - `reference_ids`,
   - `alternatives`,
   - `active_id`,
   - `status`,
   - `meta.json`.

## Validaciones ejecutadas

1. Verificación de cobertura:
   - 11 historias actualizadas.
   - 16 páginas por historia validadas.
2. Verificación de copia exacta:
   - `cover.prompt == cover_prompt` por historia.
   - `pages[].images.main.prompt == page_prompts[].main_prompt` por página.
   - `updated_at` sincronizado con el archivo de prompts.
3. Resultado:
   - `COPIED_OK=11`.

## Archivos principales tocados

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
