# Indice ADR

Los ADR registran decisiones arquitectonicas de largo plazo.

## Cuando crear un ADR

Crear ADR solo para decisiones estructurales, por ejemplo:

- gobernanza y trazabilidad del repositorio
- politica de persistencia y cache
- contrato de datos y migraciones de layout
- cambios de arquitectura con impacto transversal

## Estados permitidos

- propuesto
- aceptado
- reemplazado
- obsoleto

## ADR activos

- `docs/adr/0001-gobernanza-repositorio.md`
- `docs/adr/0003-contrato-importacion-respaldo.md`
- `docs/adr/0005-contrato-library-inbox-nnmd.md`
- `docs/adr/0006-parser-ia-asistida-gate-critico.md`
- `docs/adr/0007-canon-json-sin-sqlite-skill-editorial.md`

## ADR reemplazados

- `docs/adr/0002-politica-sqlite-local.md` (reemplazado por `0007`)
- `docs/adr/0004-biblioteca-fuente-verdad-cache-temporal.md` (reemplazado por `0007`)
