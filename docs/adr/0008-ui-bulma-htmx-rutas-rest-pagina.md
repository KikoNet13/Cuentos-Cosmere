# 0008 - UI modular Bulma+HTMX y rutas REST por pagina

- Estado: aceptado
- Fecha: 16/02/26

## Contexto

La UI estaba concentrada en pocos templates largos, con rutas de lectura/editor basadas en query (`?p=` y `?editor=1`) y sin separacion clara entre fragmentos parciales y vistas completas.

Se necesitaba:

- navegacion visual tipo catalogo por nodos con tarjetas,
- lectura limpia con opciones avanzadas ocultables,
- mantener edicion por pagina,
- estructura mantenible en frontend/backend.

## Decision

Se adopta el siguiente contrato y arquitectura de UI:

- rutas canonicas:
  - `/`
  - `/browse/<path>`
  - `/story/<path>/page/<int:page_number>`
  - `/editor/story/<path>/page/<int:page_number>`
  - `/fragments/story/<path>/page/<int:page_number>/*`
- uso de Bulma y HTMX con carga por CDN y fallback local vendor.
- backend modular por dominio en `app/web/` (`browse`, `story_read`, `story_editor`, `fragments`, `system`).
- templates Jinja modularizados en `layouts/`, `components/`, `browse/`, `story/read/`, `story/editor/`.
- compatibilidad temporal de rutas legacy con redirect:
  - `/n/<path>`
  - `/story/<path>?p=N[&editor=1]`

## Consecuencias

- mejora mantenibilidad de UI y rutas.
- lectura gana paginacion parcial HTMX y panel avanzado bajo demanda.
- editor conserva acciones de guardado/subida/activacion en rutas explicitas.
- se incrementa numero de archivos (tradeoff aceptado para evitar plantillas monoliticas).
- la compatibilidad legacy reduce friccion en enlaces existentes mientras se migra documentacion y accesos.

