# 0005 - Contrato `library/_inbox` + cuentos `NN.md`

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

El flujo operativo necesitaba simplificar la estructura canónica para ingestión desde Markdown externo y reducir pasos manuales al normalizar contenido de cada cuento.

## Decisión

Se adopta el siguiente contrato vigente:

- raíz de datos: `library/`.
- un nodo se considera libro si contiene uno o más archivos `NN.md`.
- cada cuento se representa en un único archivo `NN.md` (2 dígitos).
- estructura de `NN.md`:
  - `## Meta`
  - `## Página NN`
  - `### Texto`
  - `### Prompts`
  - `#### <slot>`
  - `##### Requisitos` (YAML tipado `tipo/ref`).
- imágenes junto al cuento con convención `<NN>-p<PP>-<slot>.png`.
- PDF de referencia junto al cuento con nombre `<NN>.pdf`.
- ingestión genérica en `library/_inbox/<batch_id>/` con flujo parsear, revisar y aplicar:
  - `python manage.py inbox-parse ...`
  - `python manage.py inbox-apply --approve`.

## Consecuencias

- Se elimina la dependencia del esquema `meta.md + NNN.md` por carpeta de cuento.
- La revisión humana queda explícita antes de aplicar cambios al canónico.
- La navegación de la app se resuelve por árbol genérico y detección de libro por `NN.md`.
- La caché SQLite sigue siendo temporal y se reconstruye tras aplicar propuestas.
