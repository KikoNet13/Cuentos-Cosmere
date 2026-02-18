# ChatGPT Project Setup - <BOOK_TITLE>

## Nombre sugerido del Project
- `<BOOK_TITLE> - Generacion de imagenes`

## Objetivo
- Generar imagenes para portada y paginas de los cuentos `NN.json`, manteniendo continuidad visual por anclas.

## Fuentes de verdad
1. `library/<book_rel_path>/meta.json`
2. `library/<book_rel_path>/NN.json`

## Instrucciones maestras (copiar en ChatGPT Project)
1. Mantener continuidad estricta de personajes, vestuario, paleta y trazo.
2. Tratar `reference_ids` como anclas visuales prioritarias del slot.
3. No inventar cambios de estilo entre paginas.
4. Mantener encuadre y tono segun prompt del slot.
5. Entregar una imagen por iteracion para facilitar seleccion editorial.

## Style Prompt Maestro de la saga
1. Prompt canonico EN (pegar literal):
   - `<STYLE_PROMPT_MAESTRO_EN_LITERAL>`
2. Resumen tecnico ES (operativo y breve):
   - `<STYLE_PROMPT_MAESTRO_ES_RESUMEN>`
3. Regla de uso:
   - reutilizar el style prompt maestro en cada turno;
   - no sustituirlo por variaciones libres.

## Modificadores de composicion (por intencion del slot)
1. Full-bleed (ilustracion completa):
   - `"Full-bleed composition, edge-to-edge illustration, cinematic 2D view"`.
2. Spot art (imagen suelta):
   - `"Isolated spot art on a clean white background, no borders, centered"`.
3. Politica:
   - aplicar modificador solo cuando el slot/prompt lo pida de forma explicita;
   - no forzar composicion por paridad de pagina.

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
2. Si falta algun bloque o el prompt es demasiado corto, NO generar imagen.
3. Solicitar delta a NotebookLM con el codigo correspondiente (`prompts.missing_sections` o `prompts.too_short`).

## Fase 1 obligatoria - anclas
1. Generar primero anclas de `meta.json` (especialmente `style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`).
2. Validar continuidad base antes de producir paginas.
3. Registrar variantes utiles como alternativas del propio anchor.

## Fase 2 - portada y paginas
1. Abrir editor de portada: `/<book>/<NN>?editor=1`.
2. Para cada slot (cover/main/secondary):
   - copiar prompt;
   - copiar refs individuales;
   - decidir composicion por intencion del slot/prompt (`full-bleed` o `spot art` solo si aplica);
   - validar que el prompt cumpla los 8 bloques;
   - generar en ChatGPT;
   - pegar en webapp con "Pegar y guardar alternativa";
   - activar alternativa elegida.

## QA rapido por pagina
1. Personajes: rasgos, edad aparente, ropa, proporciones.
2. Continuidad: objetos y escenario coherentes con paginas vecinas.
3. Composicion: accion principal clara y legible.
4. Paleta: consistente con anclas de estilo.
5. Slot correcto: imagen cargada en cover/main/secondary segun corresponda.

## Troubleshooting
1. Si falla copiar imagen desde webapp:
   - abrir imagen individual y copiar manualmente.
2. Si falla leer portapapeles:
   - confirmar HTTPS/contexto seguro o navegador compatible.
3. Si no hay refs del slot:
   - revisar `reference_ids` en el JSON o completar con anclas de estilo.
4. Si el prompt llega fuera de estandar:
   - detener generacion y pedir delta a NotebookLM;
   - no improvisar estilo fuera del contrato.
