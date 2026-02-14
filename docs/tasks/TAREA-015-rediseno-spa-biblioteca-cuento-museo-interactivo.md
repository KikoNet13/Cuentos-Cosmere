## Metadatos

- ID de tarea: `TAREA-015-rediseno-spa-biblioteca-cuento-museo-interactivo`
- Fecha: 14/02/26 16:50
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Migrar la UI web a una SPA completa con navegacion de biblioteca por nodos, lectura de cuento pagina a pagina y modo de edicion integrado, soportado por API JSON versionada en Flask.

## Contexto

La app usaba templates Jinja server-rendered (`/n/*`, `/story/*`) con modos separados lectura/editorial. El objetivo de producto exigia:

- rutas nuevas (`/biblioteca/*`, `/cuento/*`),
- experiencia visual museo interactivo,
- API `v1` con contrato uniforme,
- eliminacion de rutas legacy y frontend legacy.

## Plan

1. Separar runtime web en shell SPA + API `v1`.
2. Implementar frontend `Vue + Vite` con router y vistas Biblioteca/Cuento.
3. Integrar modo editor en la misma vista de cuento.
4. Crear tests backend con `unittest` y `Flask test_client`.
5. Actualizar documentacion operativa y trazabilidad de tarea.

## Decisiones

- Arquitectura final: SPA completa (`Vue + Vite`) con Flask como backend JSON.
- Rutas publicas nuevas: `/biblioteca/...` y `/cuento/...`; rutas legacy eliminadas.
- API versionada en `/api/v1/*` con envoltura `ok/data/error`.
- Edicion integrada en la vista de cuento (sin auth en esta fase).
- Build frontend a `app/static/spa/` con assets fijos (`app.js`, `app.css`) y carpeta compilada ignorada en git.

## Cambios aplicados

- Backend Flask:
  - `app/routes_api_v1.py` (blueprint API con endpoints de biblioteca, cuento, guardado, upload, activacion y health).
  - `app/routes_shell.py` (shell SPA, redirect raiz y media).
  - `app/routes.py` y `app/__init__.py` para registro de blueprints.
- Frontend SPA:
  - nuevo workspace `frontend/` con Vue Router, vistas y componentes.
  - estilo visual museo interactivo con tipografia CDN y animaciones.
- Limpieza legacy:
  - eliminados `app/routes_v3.py`, templates legacy y css legacy.
- Tests:
  - `tests/test_api_v1.py` con 6 casos API requeridos.
- Documentacion:
  - `README.md` y `app/README.md` alineados a SPA + API.
  - actualizacion de indice y changelog.

## Validacion ejecutada

- `npm --prefix frontend ci` -> OK.
- `npm --prefix frontend run build` -> OK.
- `python -m unittest discover -s tests` -> OK (6 tests).

## Riesgos

- El build SPA es requisito para servir UI funcional en runtime local (assets no versionados).
- No hay autenticacion para modo editor (decidido para fase actual).

## Seguimiento

- Evaluar auth ligera para endpoints mutables (`PATCH/POST/PUT`) en siguiente tarea.
- Evaluar pipeline CI para build/deploy de `app/static/spa`.

## Commit asociado

- Mensaje de commit: `Tarea 015: rediseño SPA biblioteca-cuento museo interactivo`
- Hash de commit: `pendiente`
