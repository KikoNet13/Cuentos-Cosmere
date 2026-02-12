# Flujo de revisiÃ³n (Cosmere)

## Objetivo

Mantener cuentos infantiles coherentes con el canon base, con lenguaje seguro para 7-9 aÃ±os y formato Markdown estable.

## Entrada esperada

- Texto fuente por bloque en archivos `origen_md.md` por cuento.
- Estructura por pÃ¡ginas (ideal: 32 pÃ¡ginas).
- Referencia factual local (PDF del mismo bloque) cuando se necesite validar nombres o tÃ©rminos.

## Proceso

1. Convertir el archivo a Markdown (`.md`).
2. AÃ±adir `#` (tÃ­tulo del bloque) y `## PÃ¡gina N` para cada pÃ¡gina.
3. Quitar preÃ¡mbulos de generaciÃ³n y separadores no narrativos.
4. Corregir consistencia de nombres, tÃ©rminos y reglas (sin reescritura total).
5. Suavizar lenguaje violento para pÃºblico infantil sin romper los hechos base.
6. Validar que hay 32 secciones `## PÃ¡gina N` y codificaciÃ³n UTF-8.

## Salida esperada

- Archivo `.md` limpio y legible.
- Estructura estable para iterar (revisiÃ³n textual primero, prompts de imagen despuÃ©s).

