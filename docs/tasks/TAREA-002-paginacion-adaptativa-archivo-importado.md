# TAREA-002-paginacion-adaptativa-archivo-importado

## Metadatos

- ID de tarea: `TAREA-002-paginacion-adaptativa-archivo-importado`
- Fecha: 12/02/26 14:00
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0003`

## Objetivo

Eliminar la regla fija de páginas y dejar el sistema en modo adaptativo, donde
el total depende del archivo importado.

## Contexto

La importación y la UI mantenían expectativas fijas de conteo que no eran
válidas para todos los cuentos.

## Plan

1. Retirar validación por conteo esperado.
2. Ajustar estado de UI a páginas detectadas.
3. Actualizar contrato documental.
4. Validar con comprobaciones finitas.

## Decisiones

- Parseo por encabezados `## Página N`.
- Duplicados: prevalece la última aparición.
- Huecos reportados de forma dinámica.

## Cambios aplicados

- Parser de páginas adaptativo.
- Importación/migración sin objetivo fijo.
- UI con selector según páginas detectadas.
- Actualización documental del contrato adaptativo.

## Validación ejecutada

- `python manage.py --help`
- Pruebas locales de parser con páginas no consecutivas.
- Importación de módulos Python modificados.

## Riesgos

- Si faltan encabezados `## Página N`, no hay páginas parseables.

## Seguimiento

- Añadir pruebas automatizadas para huecos y duplicados.

## Commit asociado

- Mensaje de commit: `Tarea 002: paginación adaptativa por archivo importado`
- Hash de commit: `70c556a`
