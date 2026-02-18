# Pasos operativos para generar imagenes (guia generica)

## 1) Preparacion
1. Abre la webapp del orquestador.
2. Entra en el flujo guiado de pendientes (si existe) o en el editor del cuento.
3. Verifica que el Project de ChatGPT tenga cargadas las instrucciones del archivo de setup.

## 2) Prioridad de trabajo
1. Genera primero todas las anclas pendientes.
2. Cuando no queden anclas, pasa a portadas.
3. Luego genera paginas (slot main y, si existe, slot secondary).

## 3) Gate de prompt (obligatorio)
1. Antes de generar, valida que el prompt tenga estos 8 bloques:
   - `OBJETIVO DE ILUSTRACION`
   - `CONTINUIDAD VISUAL OBLIGATORIA`
   - `COMPOSICION Y ENCUADRE`
   - `PERSONAJES Y ACCION`
   - `ENTORNO, PALETA E ILUMINACION`
   - `REFERENCIAS (reference_ids)`
   - `RESTRICCIONES / NEGATIVOS`
   - `FORMATO DE SALIDA`
2. Si falta algun bloque o el prompt es demasiado corto, no generar imagen.
3. Solicitar delta a NotebookLM (`prompts.missing_sections` o `prompts.too_short`).

## 4) Ciclo rapido por cada pendiente
1. Copia el prompt del slot/ancla desde la webapp.
2. Copia una o varias referencias necesarias.
3. Pega prompt + referencias en ChatGPT Project.
4. Genera la imagen.
5. Copia la imagen resultante.
6. Vuelve a la webapp y usa "Pegar y guardar".
7. Comprueba que la alternativa quedo activa.
8. Pasa al siguiente pendiente.

## 5) Criterios de revision inmediata
1. Continuidad de personaje: cara, pelo, ropa, proporcion.
2. Continuidad de entorno: localizacion, epoca de luz, paleta.
3. Coherencia narrativa: la escena representa el texto de esa pagina.
4. Limpieza visual: sin texto incrustado ni marcas.

## 6) Si algo falla
1. Si falla el portapapeles: vuelve a copiar y reintenta.
2. Si la imagen sale incoherente: reintenta en ChatGPT reforzando continuidad y refs.
3. Si falta contexto o el prompt viene incompleto: solicita delta a NotebookLM, no improvises fuera del estandar.

## 7) Cierre
1. Recorre el cuento completo y valida que no queden pendientes.
2. Haz una pasada final de coherencia visual entre paginas consecutivas.
3. Documenta incidencias si algun slot queda sin resolver.
