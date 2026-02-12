# Prompts de imágenes master Era 1

## Objetivo

Definir una base consistente para generar imágenes de Mistborn Era 1 con
estilo infantil y coherencia narrativa por página.

## Referencias canónicas

- `docs/context/canon_cuento_objetivo_16_paginas.md`
- `docs/assets/style_refs/Hansel y Gretel/`
- `biblioteca/.../01/textos/origen_md.md`
- `biblioteca/.../02/textos/origen_md.md`
- `biblioteca/.../03/textos/origen_md.md`

## Contrato de paginación

1. La estructura de páginas depende del archivo que importes.
2. Si el archivo trae 16 páginas, se trabajará con 16.
3. Si el archivo trae más páginas, la app conserva compatibilidad.
4. El perfil de 16 páginas es recomendado, no obligatorio.

## Reglas visuales globales

1. Mantener estilo de cuento ilustrado, no fotorealista.
2. Mantener coherencia de personajes entre escenas.
3. Sin texto incrustado, logos ni marcas de agua.
4. Sin elementos modernos fuera del mundo narrativo.
5. Violencia sugerida sin detalle gráfico.

## Flujo recomendado

1. Definir páginas desde `origen_md.md`.
2. Preparar anclas visuales de personajes principales.
3. Generar página por página respetando el texto adaptado.
4. Corregir desvíos citando ancla concreta y rasgo a ajustar.

## Plantilla de prompt por página

```text
Página: <N>
Plano: <general|medio|detalle>
Personajes: <lista>
Acción: <acción principal>
Ambiente: <luz, atmósfera y paleta>
Consistencia: igualar rasgos de anclas y vestuario base
Salida: imagen 1:1, sin texto, sin explicación adicional
```
