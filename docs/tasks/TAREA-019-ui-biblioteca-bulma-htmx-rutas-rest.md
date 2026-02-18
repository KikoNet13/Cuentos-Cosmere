# TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest

## Metadatos

- ID de tarea: `TAREA-019-ui-biblioteca-bulma-htmx-rutas-rest`
- Fecha: 16/02/26 13:44
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`, `0008`

## Objetivo

Implementar una UI de biblioteca tipo catalogo streaming con stack Jinja + Bulma + HTMX, separando lectura y edición por rutas REST de página y manteniendo compatibilidad temporal con rutas legacy.

## Contexto

La app tenia templates monoliticos y rutas de lectura/editor por query (`?p=` y `?editor=1`). Se requeria una estructura más mantenible, panel avanzado ocultable en lectura y navegación con tarjetas visuales de nodos/cuentos.

## Plan

1. Modularizar backend web por dominio de rutas y view-models.
2. Reestructurar templates en layouts/componentes/paginas.
3. Integrar Bulma + HTMX (CDN + fallback local vendor).
4. Redisenar navegación y vistas de lectura/editor con panel avanzado HTMX.
5. Actualizar contrato documental (AGENTS/README/ADR/tarea/indice/changelog).

## Decisiones

- Contrato canónico de rutas actualizado a:
  - `/`
  - `/browse/<path>`
  - `/story/<path>/page/<int:page_number>`
  - `/editor/story/<path>/page/<int:page_number>`
  - `/fragments/story/<path>/page/<int:page_number>/*`
- Se mantienen rutas legacy con redirect para transicion.
- HTMX se usa en lectura para:
  - paginación parcial con `hx-push-url`,
  - carga diferida del panel avanzado,
  - activacion de alternativa desde lectura con refresh parcial + swap OOB de imagen principal.
- Navegación de nodos se mantiene full-page para simplicidad y claridad.
- Catalogo incorpora miniatura por cuento (`cover`, luego `main` activa, luego placeholder).

## Cambios aplicados

- Backend:
  - `app/catalog_provider.py` (thumbnail de cuento y resumen enriquecido por story card).
  - `app/__init__.py` (registro de blueprint modular).
  - `app/routes_v3.py` (compat wrapper de import).
  - `app/web/__init__.py`
  - `app/web/common.py`
  - `app/web/viewmodels.py`
  - `app/web/routes_browse.py`
  - `app/web/routes_story_read.py`
  - `app/web/routes_story_editor.py`
  - `app/web/routes_fragments.py`
  - `app/web/routes_system.py`
- Templates:
  - `app/templates/layouts/base.html`
  - `app/templates/components/*`
  - `app/templates/browse/page.html`
  - `app/templates/story/read/*`
  - `app/templates/story/editor/page.html`
  - Eliminados templates legacy monoliticos (`base`, `dashboard`, `node`, `cuento_read`, `cuento_editor`).
- Frontend static:
  - `app/static/css/app.css`
  - `app/static/css/tokens.css`
  - `app/static/css/layout.css`
  - `app/static/css/components.css`
  - `app/static/css/pages.css`
  - `app/static/js/clipboard.js`
  - `app/static/js/story_read.js`
  - `app/static/vendor/bulma.min.css`
  - `app/static/vendor/htmx.min.js`
- Documentacion:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/adr/0008-ui-bulma-htmx-rutas-rest-pagina.md`
  - `docs/adr/INDICE.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

1. `python -m compileall app`
2. `python manage.py --help`
3. `python manage.py runserver --help`
4. `python -c "from app import create_app; c=create_app().test_client(); print('/', c.get('/').status_code); print('/browse', c.get('/browse').status_code); print('/health', c.get('/health').status_code); print('/n/ejemplo', c.get('/n/ejemplo').status_code)"`
   - Resultado observado: `/=200`, `/browse=302`, `/health=200`, `/n/ejemplo=302`.

## Riesgos

- El fallback CDN->local de Bulma/HTMX depende de carga de assets externos y del probe en cliente.
- En biblioteca vacia no hay flujo completo de lectura/edicion de cuento real para smoke test end-to-end.

## Seguimiento

1. Agregar tests Flask basicos de rutas canónicas y redirects legacy.
2. Evaluar retiro definitivo de rutas legacy tras migrar bookmarks/enlaces operativos.

## Commit asociado

- Mensaje de commit: `Tarea 019: UI biblioteca Bulma HTMX con rutas REST por pagina`
- Hash de commit: pendiente

