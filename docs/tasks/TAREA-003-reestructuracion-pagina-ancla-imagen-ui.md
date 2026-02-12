# TAREA-003-reestructuracion-pagina-ancla-imagen-ui

## Metadatos

- ID de tarea: TAREA-003-reestructuracion-pagina-ancla-imagen-ui
- Fecha: 12/02/26 14:41
- Estado: cerrada
- Responsable: local
- ADR relacionadas: 0003

## Objetivo

Reestructurar el dominio y la interfaz para centrar el flujo en generación
visual por página, con referencias semánticas versionables por saga.

## Contexto

El sistema mantenía un dominio legacy (`Texto`, `Prompt`, `ImagenPrompt`)
que mezclaba edición textual y prompts en tarjetas masivas. Se necesitaba
un modelo explícito de página e imagen, más una gestión formal de anclas
versionadas y requisitos visuales.

## Plan

1. Introducir modelos `Pagina`, `Ancla`, `AnclaVersion`, `Imagen` e
   `ImagenRequisito`.
2. Implementar migración `migrate-models-v3` idempotente.
3. Adaptar importador a `Pagina` con upsert por número y borrado de sobrantes.
4. Rehacer backend/UI de cuento a navegación por página.
5. Añadir pantalla de gestión de anclas por saga.
6. Actualizar CLI y documentación.

## Decisiones

- `Prompt` e `ImagenPrompt` pasan a legado migrado y fuera de dominio activo.
- `Imagen` pertenece de forma exclusiva a `Pagina` o `AnclaVersion`.
- Principal activa estricta por página mediante índice único parcial.
- Requisitos mixtos: referencia a `AnclaVersion` o a `Imagen`.
- `import` sigue limitado a páginas/PDF y elimina páginas no presentes.

## Cambios aplicados

- Modelos y esquema:
  - `app/models.py`
  - `app/db.py`
  - `app/importer.py`
  - `app/config.py`
  - `manage.py`
- Backend web v3:
  - `app/routes_v3.py`
  - `app/routes.py`
- UI:
  - `app/templates/cuento.html`
  - `app/templates/anclas.html`
  - `app/templates/dashboard.html`
  - `app/templates/saga.html`
  - `app/templates/libro.html`
  - `app/templates/base.html`
- Documentación:
  - `README.md`
  - `app/README.md`
  - `docs/adr/0003-contrato-importacion-respaldo.md`
  - `docs/context/INDICE.md`
  - `docs/context/prompts_imagenes_master_era1.md`

## Validación ejecutada

- `python manage.py --help`
- `python manage.py migrate-models-v3 --help`
- `python manage.py import --help`
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -c "import manage, app.models,
  app.db, app.importer, app.routes_v3, app.routes; print('ok')"`
- `python manage.py migrate-models-v3` (2 veces, verificando idempotencia)
- `python manage.py import`

## Riesgos

- Quedan plantillas parciales legacy en repositorio sin uso activo.
- El copiado de imagen al portapapeles depende de soporte del navegador
  (hay fallback de mensaje y apertura manual).

## Seguimiento

- Añadir pruebas automáticas para restricciones de pertenencia en `Imagen` y
  `ImagenRequisito`.
- Añadir pruebas de integración para flujo de requisitos mixtos en UI.

## Commit asociado

- Mensaje de commit: `Tarea 003: reestructurar modelos y UI para generación`
- Hash de commit: `pendiente`