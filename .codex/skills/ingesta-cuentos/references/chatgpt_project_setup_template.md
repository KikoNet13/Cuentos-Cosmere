# ChatGPT Project Setup - <BOOK_TITLE>

## Nombre sugerido del Project
- `<BOOK_TITLE> - Generacion de imagenes`

## Objetivo
- Generar imágenes para portada y páginas de los cuentos `NN.json`, manteniendo continuidad visual por anclas.

## Fuentes de verdad
1. `library/<book_rel_path>/meta.json`
2. `library/<book_rel_path>/NN.json`

## Adjuntos globales del Project
1. Cargar una vez todas las anclas globales (`style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`) usando los slugs canónicos.
2. Mantener esos adjuntos durante toda la saga; no repetirlos en cada turno.

## Instrucciones maestras (copiar en ChatGPT Project)
1. Mantener continuidad estricta de personajes, vestuario, paleta y trazo.
2. Tratar `reference_ids` del slot como contexto de escena (máximo 6), no como pack global.
3. No repetir `style_linea_editorial` ni `style_paleta_rebelion` por slot si ya están como adjuntos globales.
4. No inventar cambios de estilo entre páginas.
5. Mantener encuadre y tono según prompt del slot.
6. Entregar una imagen por iteración para facilitar selección editorial.

## Style Prompt Maestro de la saga
1. Prompt canónico EN (pegar literal):
   - `<STYLE_PROMPT_MAESTRO_EN_LITERAL>`
2. Resumen técnico ES (operativo y breve):
   - `<STYLE_PROMPT_MAESTRO_ES_RESUMEN>`
3. Regla de uso:
   - reutilizar el style prompt maestro en cada turno;
   - no sustituirlo por variaciones libres.

## Modificadores de composición (por intención del slot)
1. Full-bleed (ilustración completa):
   - `"Full-bleed composition, edge-to-edge illustration, cinematic 2D view"`.
2. Spot art (imagen suelta):
   - `"Isolated spot art on a clean white background, no borders, centered"`.
3. Política:
   - aplicar modificador solo cuando el slot/prompt lo pida de forma explícita;
   - no forzar composición por paridad de página.

## Gate obligatorio de prompt (antes de generar)
1. El prompt de cada slot debe incluir los 8 bloques:
   - `OBJETIVO DE ILUSTRACION`
   - `CONTINUIDAD VISUAL OBLIGATORIA`
   - `COMPOSICION Y ENCUADRE`
   - `PERSONAJES Y ACCION`
   - `ENTORNO, PALETA E ILUMINACION`
   - `REFERENCIAS (reference_ids)`
   - `RESTRICCIONES / NEGATIVOS`
   - `FORMATO DE SALIDA`
2. Si falta algún bloque o el prompt es demasiado corto, NO generar imagen.
3. Solicitar delta a NotebookLM con el código correspondiente (`prompts.missing_sections` o `prompts.too_short`).

## Fase 1 obligatoria - anclas
1. Generar primero anclas de `meta.json`.
2. Validar continuidad base antes de producir páginas.
3. Registrar variantes útiles como alternativas del propio anchor.

## Fase 2 - portada y páginas
1. Abrir editor de portada: `/<book>/<NN>?editor=1`.
2. Para cada slot (cover/main/secondary):
   - copiar prompt;
   - copiar refs de escena;
   - decidir composición por intención del slot/prompt (`full-bleed` o `spot art` solo si aplica);
   - validar que el prompt cumpla los 8 bloques;
   - generar en ChatGPT;
   - pegar en webapp con "Pegar y guardar alternativa";
   - activar alternativa elegida.

## QA rápido por página
1. Personajes: rasgos, edad aparente, ropa, proporciones.
2. Continuidad: objetos y escenario coherentes con páginas vecinas.
3. Composición: acción principal clara y legible.
4. Paleta: consistente con anclas de estilo.
5. Slot correcto: imagen cargada en cover/main/secondary según corresponda.

## Troubleshooting
1. Si falla copiar imagen desde webapp:
   - abrir imagen individual y copiar manualmente.
2. Si falla leer portapapeles:
   - confirmar HTTPS/contexto seguro o navegador compatible.
3. Si no hay refs del slot:
   - revisar `reference_ids` en el JSON (manteniendo cap 6 y filtro semántico).
4. Si el prompt llega fuera de estándar:
   - detener generación y pedir delta a NotebookLM;
   - no improvisar estilo fuera del contrato.
