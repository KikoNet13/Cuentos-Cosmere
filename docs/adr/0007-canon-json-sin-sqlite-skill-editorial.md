# 0007 - Canon `NN.json` sin SQLite y skill editorial

- Estado: aceptado
- Fecha: 13/02/26

## Contexto

El flujo con `NN.md` + cache SQLite + comandos CLI de ingesta generaba complejidad operativa innecesaria para el trabajo editorial diario.

## Decision

Se adopta el siguiente contrato vigente:

- fuente de verdad: `library/.../NN.json`.
- un libro se detecta por presencia de archivos `NN.json`.
- cada cuento vive en un único archivo `NN.json`.
- estructura por página:
  - `text.original` y `text.current`
  - `images.main` obligatorio
  - `images.secondary` opcional
- cada slot de imagen define `prompt.original/current`, `alternatives[]` y `active_id`.
- la webapp navega por escaneo directo de disco.
- SQLite deja de participar en runtime de lectura/navegacion.
- no hay CLI de ingesta; el flujo oficial se ejecuta mediante skill `revision-orquestador-editorial`.

## Consecuencias

- se simplifica la operación diaria de ingesta/adaptacion editorial.
- la comparativa original/current queda integrada en el contrato de cuento.
- la gestion de alternativas de imagen se vuelve trazable por JSON.
- se mantiene una seam técnica para introducir índice global en el futuro sin cambiar contrato de datos.

