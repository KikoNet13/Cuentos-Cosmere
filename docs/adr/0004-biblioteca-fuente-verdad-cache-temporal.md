# 0004 - Biblioteca como fuente de verdad y cache temporal

- Estado: reemplazado por `0007`
- Fecha: 12/02/26

## Contexto

Se adopto inicialmente una arquitectura hibrida: `library/` como fuente de verdad y SQLite como cache temporal.

## Decision (historica)

- fuente de verdad canónica: `library/`
- SQLite como cache de lectura rapida
- deteccion stale por fingerprint

## Estado actual

Este ADR queda reemplazado por `0007`: la navegación pasa a lectura directa de `NN.json`, sin cache SQLite en runtime.
