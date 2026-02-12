# 0004 - Biblioteca como fuente de verdad y caché temporal

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

El modelo relacional duplicaba información que ya existía en archivos de
`biblioteca/`, complicando edición y sincronización.

## Decisión

Adoptar arquitectura híbrida con prioridad de archivos:

- fuente de verdad canónica: `biblioteca/`.
- contrato de cuento: `meta.md` + `NNN.md`.
- narrativa y prompts se editan solo en Markdown.
- SQLite se mantiene únicamente como caché temporal de lectura rápida.
- desactualización detectada por fingerprint global de `biblioteca/`.
- la UI bloquea guardado de imágenes cuando la caché está stale.

## Consecuencias

- navegación por árbol genérico, sin jerarquías fijas de dominio.
- comandos operativos centrados en migración de layout y caché.
- mayor transparencia para revisión y control del contenido canónico.
