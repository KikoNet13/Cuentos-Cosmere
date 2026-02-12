# Flujo de revisi?n Cosmere

## Objetivo

Mantener cuentos infantiles coherentes con el canon base, con lenguaje seguro
para 7-9 a?os y formato Markdown estable.

## Entrada esperada

- Texto fuente en `origen_md.md` por cuento.
- Estructura por p?ginas con objetivo de 32 p?ginas.
- Referencia factual local (`referencia_pdf.pdf`) cuando aplique.

## Proceso

1. Convertir o normalizar el texto fuente a Markdown.
2. A?adir `#` de t?tulo y `## P?gina N` para cada p?gina.
3. Retirar pre?mbulos de generaci?n y separadores no narrativos.
4. Corregir consistencia de nombres, t?rminos y reglas.
5. Suavizar lenguaje violento sin romper hechos can?nicos.
6. Verificar estructura de 32 p?ginas y codificaci?n UTF-8 sin BOM.

## Salida esperada

- Archivo `.md` limpio y legible.
- Estructura estable para iteraci?n.
- Base lista para prompts de imagen por p?gina.
