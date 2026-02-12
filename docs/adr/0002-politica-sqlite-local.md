# 0002 - Política local de persistencia SQLite

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

SQLite se usa localmente para estado temporal. Ese estado depende del entorno
y no debe versionarse en Git.

## Decisión

Mantener SQLite en `db/` y excluir de versionado:

- `db/*.sqlite`
- `db/*.sqlite-shm`
- `db/*.sqlite-wal`

## Consecuencias

- El repositorio se mantiene limpio y portable.
- El estado local no queda preservado por Git.
- Los respaldos de datos deben gestionarse fuera de SQLite.
