# 0003 - Contrato de importacion y respaldo

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

Los cuentos requieren una estructura estable para texto por pagina,
referencias versionables y generacion de imagenes con trazabilidad.

## Decision

Adoptar el contrato v3:

- La narrativa se modela en `Pagina` (por `numero` dentro de `Cuento`).
- La referencia semantica se modela con `Ancla` + `AnclaVersion` por saga.
- La generacion visual se modela con `Imagen` e `ImagenRequisito`.
- `manage.py import` sincroniza solo paginas y referencias PDF.
- El backup oficial de visuales usa `export-imagenes` / `import-imagenes`.

## Consecuencias

- Se elimina el dominio activo legacy `Prompt` + `ImagenPrompt`.
- La UI se centra en navegacion por pagina e imagenes asociadas.
- Se conserva compatibilidad operativa con alias de comandos legacy
  marcados como deprecados.