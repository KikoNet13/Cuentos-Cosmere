# 0003 - Contrato de importación y respaldo

- Estado: reemplazado por `0005`
- Fecha: 12/02/26

## Contexto

El sistema necesita un contrato estable para narrativa por página, prompts de
imagen y referencias visuales con trazabilidad.

## Decisión

Se adoptó inicialmente un contrato canónico de archivos:

- narrativa y prompts en `biblioteca/`.
- cuento canónico: `meta.md` + páginas `NNN.md`.
- frontmatter en castellano para contenido (`pagina`, `imagenes`, `requisitos`).
- referencia PDF canónica: `referencia.pdf`.
- reconstrucción de caché con `python manage.py rebuild-cache`.

## Consecuencias

- Se simplifica edición manual del contenido.
- Se elimina dependencia de modelos relacionales como fuente de verdad.
- El flujo operativo depende de migración de layout y refresco de caché.

## Estado actual

Este ADR queda reemplazado por `0005`, que define el contrato vigente:

- raíz `library/`
- cuentos en archivo único `NN.md`
- flujo `library/_inbox` con parsear/revisar/aplicar
