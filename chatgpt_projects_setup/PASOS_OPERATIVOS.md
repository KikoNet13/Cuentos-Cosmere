# Pasos operativos para generar imagenes (Project aislado)

## 1) Preparacion del Project
1. Crea/abre el Project de ChatGPT de la saga.
2. Pega como `Instructions` el contenido de `Los juegos del hambre - Imagenes editoriales (16p).md`.
3. Adjunta como contexto:
   - 27 imagenes de anclas (PNG) con nombre exacto por slug.
   - `Los juegos del hambre - Adjuntos globales (27 anclas).md`.
4. No uses rutas locales del repo en mensajes al Project.

## 2) Que enviar en cada turno
1. Prompt del slot.
2. `reference_ids` del slot (maximo 6, solo contexto de escena).
3. Si aplica, una nota corta de contexto narrativo.

## 3) Gate de prompt (obligatorio)
1. Valida los 8 bloques antes de generar:
   - `OBJETIVO DE ILUSTRACION`
   - `CONTINUIDAD VISUAL OBLIGATORIA`
   - `COMPOSICION Y ENCUADRE`
   - `PERSONAJES Y ACCION`
   - `ENTORNO, PALETA E ILUMINACION`
   - `REFERENCIAS (reference_ids)`
   - `RESTRICCIONES / NEGATIVOS`
   - `FORMATO DE SALIDA`
2. Si falta un bloque o el prompt es corto: pedir delta a NotebookLM (`prompts.missing_sections` o `prompts.too_short`).

## 4) Produccion por orden
1. Primero anclas.
2. Luego portada.
3. Luego paginas (`main`, y `secondary` solo si existe).

## 5) QA rapido
1. Coherencia de personajes (rasgos, edad, vestuario, proporciones).
2. Coherencia de entorno/props con paginas vecinas.
3. Accion principal legible en 1 vistazo.
4. Paleta y acabado estables.
5. Sin texto incrustado, logos, firmas ni marcas de agua.

## 6) Integracion externa (fuera del Project)
1. Descarga la imagen final generada.
2. Subela en tu herramienta editorial al slot correspondiente.
3. Activa la alternativa elegida y continua con el siguiente pendiente.
