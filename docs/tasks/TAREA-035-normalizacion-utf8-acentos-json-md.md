# TAREA-035 - Normalización global UTF-8 y corrección integral de acentos/ñ en `.md` y `.json`

- Fecha: 18/02/26 23:05
- Estado: cerrada
- Versión objetivo: 2.7.5

## Resumen

Se ejecuta una pasada global sobre todos los `.md` y `.json` versionados para:

1. normalizar codificación a UTF-8 sin BOM,
2. reparar mojibake residual,
3. corregir ortografía en español (acentos y ñ) en texto natural,
4. preservar contratos técnicos, rutas, comandos y literales en código/backticks.

## Alcance aplicado

1. Incluye: `git ls-files "*.md" "*.json"` (72 archivos).
2. Excluye: no versionados.
3. Incluye placeholders `*_prompts.json` como texto operativo.

## Implementación

1. Normalización en lote:
   - decodificación UTF-8 (`utf-8-sig`),
   - escritura UTF-8 sin BOM,
   - normalización Unicode NFC.
2. Reparación de mojibake:
   - secuencias tipo `Ã¡`, `Ã©`, `Ã±`, `Â¿`, `Â¡`, etc.
3. Corrección ortográfica por diccionario en lenguaje natural:
   - `imagenes→imágenes`, `pagina→página`, `paginas→páginas`, `generacion→generación`, `composicion→composición`, `iluminacion→iluminación`, `accion→acción`, `coleccion→colección`, `tecnico→técnico`, `canonico→canónico`, `version→versión`, `edicion→edición`, `operacion→operación`, `unico→único`, `valido→válido`, `mas→más`, `aun→aún`, `camara→cámara`, `camaras→cámaras`, `pais→país`.
4. Reglas de seguridad lingüística:
   - sin tocar bloques fenced de Markdown,
   - sin tocar texto entre backticks inline.

## Validaciones ejecutadas

1. Estado UTF-8:
   - `BAD_UTF8=0`
   - `WITH_BOM=0`
   - `WITH_REPL=0`
2. Mojibake:
   - `MOJIBAKE_FILES=0`
3. JSON parseable (excluyendo `*_prompts.json`):
   - `JSON_FILES_CHECKED=0`
   - `JSON_BAD=0`
4. Revisión manual de diff:
   - verificación de preservación de literales técnicos en rutas/comandos entre backticks.

## Archivos principales tocados

- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
- `docs/tasks/TAREA-035-normalizacion-utf8-acentos-json-md.md`
- resto de `.md/.json` versionados normalizados por lote.
