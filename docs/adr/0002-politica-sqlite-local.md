# 0002 - Política local de persistencia SQLite

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

La aplicación usa SQLite local para estado de ejecución.
Ese estado depende del entorno y no debe contaminar el historial Git.

## Decisión

Mantener SQLite en `db/` y excluir de versionado:

- `db/*.sqlite`
- `db/*.sqlite-shm`
- `db/*.sqlite-wal`

## Consecuencias

- El repositorio se mantiene limpio y portable.
- El estado local no queda preservado por Git.
- Los respaldos y exportaciones pasan a ser obligatorios.
