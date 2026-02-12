# 0002 - Pol?tica local de persistencia SQLite

- Estado: aceptado
- Fecha: 2026-02-12

## Contexto

La aplicaci?n usa SQLite local para estado de ejecuci?n.
Ese estado depende del entorno y no debe contaminar el historial Git.

## Decisi?n

Mantener SQLite en `db/` y excluir de versionado:

- `db/*.sqlite`
- `db/*.sqlite-shm`
- `db/*.sqlite-wal`

## Consecuencias

- El repositorio se mantiene limpio y portable.
- El estado local no queda preservado por Git.
- Los respaldos y exportaciones pasan a ser obligatorios.
