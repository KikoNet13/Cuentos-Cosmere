# 0004 - Biblioteca como fuente de verdad y caché temporal

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

El modelo relacional se había convertido en fuente principal de contenido
(`texto`, `prompt`, `imagen`), lo que duplicaba información que ya vivía en
archivos de `biblioteca/`. Esa duplicidad complicaba edición manual, revisión
y trazabilidad del material narrativo.

## Decisión

Adoptar un modelo híbrido con prioridad de archivos:

- Fuente de verdad canónica: `biblioteca/`.
- Contrato de cuento: `meta.md` + páginas `NNN.md`.
- Narrativa y prompts se editan solo en Markdown.
- SQLite se mantiene únicamente como caché temporal de lectura rápida.
- Se detecta desactualización por fingerprint global de `biblioteca/`.
- La UI bloquea guardado de imágenes cuando la caché está stale.

## Consecuencias

- Se elimina dependencia de jerarquías fijas (`saga/libro/cuento`) en la UI.
- La navegación pasa a árbol genérico por rutas de carpeta.
- Se añade migración de layout legacy con `migrate-library-layout`.
- `import` queda como alias deprecado para transición.
