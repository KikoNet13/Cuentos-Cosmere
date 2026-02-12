# 0003 - Contrato de importación y respaldo

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

Los cuentos requieren una estructura estable para texto por página,
referencias versionables y generación de imágenes con trazabilidad.

## Decision

Adoptar el contrato v3:

- La narrativa se organiza por página (`NNN.md`) en `biblioteca/`.
- La referencia semántica puede modelarse con anclas/versiones de apoyo.
- La generación visual se define por slots de imagen por página.
- El refresco operativo usa caché temporal (`rebuild-cache`).
- El respaldo legacy de visuales sigue disponible para transición.

## Consecuencias

- Se elimina el dominio activo legacy `Prompt` + `ImagenPrompt`.
- La UI se centra en navegación por página e imágenes asociadas.
- Se conserva compatibilidad operativa con alias de comandos legacy
  marcados como deprecados.
