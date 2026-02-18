# TAREA-038 - Fix `Request Entity Too Large` en "Pegar y guardar"

- Fecha: 19/02/26 00:50
- Estado: cerrada
- Version objetivo: 2.7.8

## Resumen

Se corrige el error `413 Request Entity Too Large` al usar acciones de "Pegar y guardar", migrando el envio preferente de imagen pegada a `multipart/form-data` con `image_file`, y elevando limites de request en backend a 20 MB.

## Alcance aplicado

1. Backend:
   - `MAX_CONTENT_LENGTH = 20 MB`
   - `MAX_FORM_MEMORY_SIZE = 20 MB`
   - `errorhandler` explicito para `RequestEntityTooLarge` con flash y redireccion util.
2. Frontend:
   - `pasteImageAndSubmit(...)` ahora:
     - lee blob del portapapeles,
     - construye `FormData(form)`,
     - elimina `pasted_image_data` en envio principal,
     - adjunta `image_file` (`pasted-<timestamp>.<ext>`),
     - envia por `fetch` y navega a la URL final.
   - Fallback legacy preservado cuando `fetch`/`FormData` no estan disponibles.
3. Compatibilidad:
   - `extract_image_payload(...)` no cambia y mantiene soporte de `image_file` + fallback base64.

## Validaciones ejecutadas

1. Configuracion de app:
   - `MAX_CONTENT_LENGTH = 20971520`
   - `MAX_FORM_MEMORY_SIZE = 20971520`
2. Manejo 413:
   - request con payload >20 MB devuelve redireccion y evita pagina generica de werkzeug.
3. Cola de flujo:
   - sin cambios de contrato de datos ni rutas de persistencia.

## Archivos tocados

- `app/config.py`
- `app/__init__.py`
- `app/static/js/clipboard.js`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
- `docs/tasks/TAREA-038-fix-request-entity-too-large-pegar-guardar.md`
