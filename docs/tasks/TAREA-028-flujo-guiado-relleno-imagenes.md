# TAREA-028 - Flujo guiado de relleno de imágenes pendientes

- Fecha: 18/02/26 17:12
- Estado: cerrada
- Versión objetivo: 2.5.0

## Resumen

Se implementa un modo operativo único para produccion de imágenes:

1. Se entra por `/_flow/image`.
2. La app muestra solo el primer pendiente global.
3. Se copia prompt/referencias, se genera en ChatGPT, se pega y guarda.
4. Al guardar, la vista recarga y muestra el siguiente pendiente.

La prioridad de cola queda cerrada: anclas primero, despues cuentos.

## Alcance implementado

1. Motor de cola global:
   - nuevo módulo `app/web/image_flow.py`.
   - recorre `library/**/meta.json` y cuentos `NN.json` excluyendo `_inbox`, `_processed`, `_backups`.
   - criterio de pendiente:
     - `status != not_required`,
     - prompt no vacio,
     - sin imagen activa válida.
   - excluidos:
     - prompt vacio.
2. Orden de cola:
   - bloque 1: anclas (`node_rel_path`, `anchor_id`).
   - bloque 2: cuentos por `story_rel_path`:
     - `cover`,
     - `main` 1..N,
     - `secondary` 1..N.
3. Rutas nuevas:
   - `GET /_flow/image`
   - `POST /_flow/image/submit`
4. Guardado rapido:
   - alta de alternativa segun tipo (`anchor`, `cover`, `slot`);
   - activacion inmediata de la alternativa recien creada para cerrar el pendiente;
   - redireccion al mismo flujo para mostrar el siguiente.
5. Reuso de helper de imagen pegada:
   - nuevo `app/web/image_upload.py`;
   - `routes_story_editor.py` migra a ese helper comun.
6. UI:
   - nuevo template `app/templates/story/flow/image_fill.html` (modo minimal de produccion).
   - topbar con acceso directo y badge de pendientes.
7. Integración de blueprint:
   - registro de `routes_image_flow` en `app/web/__init__.py`.
   - context processor global para estado de pendientes en topbar.

## Validaciones ejecutadas

1. Sintaxis Python:
   - `python -m compileall app`
2. Rutas y endpoints:
   - inspeccion de reglas Flask via `app.test_request_context` + `url_map`.
3. Verificacion de cambios:
   - `git diff -- <archivos tocados>`
   - `git status --short`

## Archivos principales tocados

- `app/web/image_flow.py`
- `app/web/image_upload.py`
- `app/web/routes_image_flow.py`
- `app/web/routes_story_editor.py`
- `app/web/__init__.py`
- `app/templates/components/topbar.html`
- `app/templates/story/flow/image_fill.html`
- `app/static/css/pages.css`
- `AGENTS.md`
- `docs/guia-orquestador-editorial.md`
- `docs/tasks/TAREA-028-flujo-guiado-relleno-imagenes.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
