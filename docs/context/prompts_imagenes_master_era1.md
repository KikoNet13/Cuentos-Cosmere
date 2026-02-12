# Prompts e imagenes master (Era 1)

## Contrato operativo v3

- Cada pagina del cuento tiene su texto en `Pagina`.
- Las imagenes se gestionan en `Imagen` por pagina.
- Las referencias canonicas viven en `AnclaVersion`.
- Los requisitos de una imagen pueden apuntar a `AnclaVersion` o `Imagen`.

## Flujo recomendado

1. Importar paginas desde `origen_md.md`.
2. Navegar cuento pagina a pagina.
3. Redactar `prompt_texto` por imagen.
4. Adjuntar requisitos con referencias visuales.
5. Copiar imagenes de referencia desde la UI al portapapeles.

## Referencia visual

- Canon editorial: `docs/context/canon_cuento_objetivo_16_paginas.md`
- Muestras de estilo: `docs/assets/style_refs/Hansel y Gretel/`

## Nota

El sistema no impone un total fijo de paginas. El archivo importado define
el numero real de paginas del cuento.