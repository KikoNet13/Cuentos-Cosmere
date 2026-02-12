# Prompts e imágenes master (Era 1)

## Contrato operativo actual

1. La narrativa y prompts viven en archivos Markdown de `biblioteca/`.
2. Cada página (`NNN.md`) contiene texto y slots de imagen en frontmatter.
3. La UI solo consume ese contenido para lectura/copia y guardado de imagen.
4. Las referencias visuales se resuelven desde rutas de requisitos.

## Flujo recomendado

1. Editar narrativa/prompts en `biblioteca/.../<cuento>/NNN.md`.
2. Ejecutar `python manage.py rebuild-cache`.
3. Navegar a la página del cuento en la UI.
4. Copiar texto/prompt/referencias y generar imagen fuera de la app.
5. Subir o pegar imagen generada en el slot correspondiente.

## Referencias

- Canon editorial recomendado: `docs/context/canon_cuento_objetivo_16_paginas.md`
- Referencia visual: `docs/assets/style_refs/Hansel y Gretel/`
