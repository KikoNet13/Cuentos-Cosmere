# Pasos operativos para generar imágenes

## 1) Preparación inicial del Project
1. Crea/abre el Project de ChatGPT para la saga.
2. Carga como adjuntos globales las 27 anclas con su slug exacto (una sola vez).
3. Usa como manifiesto: `chatgpt_projects_setup/Los juegos del hambre - Adjuntos globales (27 anclas).md`.
4. Pega las instrucciones maestras del archivo de setup del Project.

## 2) Prioridad de trabajo
1. Genera primero todas las anclas pendientes.
2. Cuando no queden anclas, pasa a portadas.
3. Luego genera páginas (`main` y `secondary` solo si existe).

## 3) Gate de prompt (obligatorio)
1. Antes de generar, valida los 8 bloques del prompt:
   - `OBJETIVO DE ILUSTRACIÓN`
   - `CONTINUIDAD VISUAL OBLIGATORIA`
   - `COMPOSICIÓN Y ENCUADRE`
   - `PERSONAJES Y ACCIÓN`
   - `ENTORNO, PALETA E ILUMINACIÓN`
   - `REFERENCIAS (reference_ids)`
   - `RESTRICCIONES / NEGATIVOS`
   - `FORMATO DE SALIDA`
2. Si falta un bloque o el prompt es corto, no generes imagen.
3. Solicita delta a NotebookLM con `prompts.missing_sections` o `prompts.too_short`.

## 4) Reglas operativas de `reference_ids`
1. `reference_ids` del slot son contexto de escena, no adjuntos globales.
2. Máximo 6 referencias por slot.
3. No repetir `style_linea_editorial` ni `style_paleta_rebelion` en slots si ya están como adjuntos globales.
4. Filtrado semántico: solo personajes/props/entornos presentes en el texto/prompt de la escena (o continuidad explícita).

## 5) Ciclo rápido por cada pendiente
1. Copia el prompt del slot/ancla desde la webapp.
2. Copia los `reference_ids` del slot (si aplica).
3. Pega en ChatGPT Project y genera la imagen.
4. Vuelve a la webapp y usa "Pegar y guardar".
5. Verifica que la alternativa quedó activa.
6. Continúa con el siguiente pendiente.

## 6) QA rápido por página
1. Coherencia de personajes (rasgos, edad, ropa, proporción).
2. Coherencia de entorno/props entre páginas adyacentes.
3. Acción principal clara y legible.
4. Paleta y acabado estables en todo el bloque narrativo.
5. Sin texto incrustado, logos ni marcas de agua.

## 7) Cierre
1. Revisa que no queden pendientes en `/_flow/image`.
2. Haz pasada de continuidad por cuento completo.
3. Registra incidencias si algún slot queda sin resolver.
