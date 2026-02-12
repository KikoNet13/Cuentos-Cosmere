# TAREA-002-paginacion-adaptativa-archivo-importado

## Metadatos

- ID de tarea: TAREA-002-paginacion-adaptativa-archivo-importado
- Fecha: 12/02/26 14:00
- Estado: cerrada
- Responsable: local
- ADR relacionadas: 0003

## Objetivo

Eliminar la regla fija de páginas y dejar la aplicación en modo
adaptativo, donde la cantidad de páginas depende del archivo
`origen_md.md` importado.

## Contexto

El sistema arrastraba una expectativa fija de conteo de páginas en
importación y en estado de UI. El objetivo acordado fue mantener
compatibilidad con archivos de 16, 32 o cualquier otro total válido,
sin truncado ni warnings por conteo esperado.

## Plan

1. Retirar la dependencia a `EXPECTED_PAGE_COUNT`.
2. Ajustar importación, migración y estado de UI a paginación adaptativa.
3. Actualizar mensajes y documentación del contrato.
4. Validar con comprobaciones finitas.

## Decisiones

- Mantener el parseo por encabezados `## Página N`.
- Mantener la regla de duplicados: prevalece la última aparición.
- Mostrar páginas disponibles según DB y reportar huecos dinámicos.
- El perfil editorial de 16 páginas queda como recomendación, no regla.

## Cambios aplicados

- `app/text_pages.py`: eliminación de objetivo fijo de páginas.
- `app/importer.py`: importación y migración sin validación por conteo
  esperado.
- `app/routes.py`: estado de textos adaptativo a páginas detectadas.
- `app/templates/cuento.html`: copia de interfaz ajustada a modo
  adaptativo.
- `app/templates/partials/texts_list.html`: aviso de faltantes dinámico.
- `docs/context/canon_cuento_objetivo_16_paginas.md`: documento canónico
  del perfil visual/editorial recomendado.
- `docs/context/prompts_imagenes_master_era1.md`: alineación con contrato
  adaptativo.
- `docs/context/INDICE.md`, `docs/assets/style_refs/INDICE.md`,
  `README.md`, `app/README.md`, `AGENTS.md`, `docs/adr/0003-*.md`:
  actualización de referencias y contrato documental.
- `biblioteca/**/origen_md.md`: sin cortes de línea forzados por
  formato.

## Validación ejecutada

- `python manage.py --help`
- Prueba local del parser con muestra `## Página 1`, `## Página 2`,
  `## Página 4` y verificación de resultado.
- `$env:PYTHONDONTWRITEBYTECODE='1'; python -c "import app.text_pages,
  app.importer, app.routes; print('ok')"`

## Riesgos

- Si un archivo no respeta el encabezado `## Página N`, no habrá páginas
  detectables y el importador emitirá warning.

## Seguimiento

- Añadir test automatizado para casos de huecos y duplicados en páginas.
- Definir, si se desea, una validación opcional de perfil editorial
  recomendado (warning) desacoplada de la importación.

## Commit asociado

- Mensaje de commit: `Tarea 002: paginación adaptativa por archivo importado`
- Hash de commit: `pendiente`