# 0002 - Politica local de persistencia SQLite

- Estado: reemplazado por `0007`
- Fecha: 12/02/26

## Contexto

SQLite se usaba localmente para estado temporal no versionado.

## Decision (historica)

Mantener SQLite en `db/` y excluir de versionado.

## Estado actual

Este ADR queda reemplazado por `0007`, que elimina SQLite del runtime de navegacion y adopta lectura directa desde `NN.json`.
