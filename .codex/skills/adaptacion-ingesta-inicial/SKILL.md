---
name: adaptacion-ingesta-inicial
description: Skill conversacional para ingesta inicial de propuestas en library/_inbox (NN.md + NN.pdf) hacia NN.json y sidecars de contexto/issues con contraste canonico obligatorio.
---

# Adaptacion Ingesta Inicial

## Objetivo
Convertir propuestas de `library/_inbox/<book>/NN.md` + `NN.pdf` a:
- `library/<book_rel_path>/NN.json`
- `library/<book_rel_path>/_reviews/adaptation_context.json`
- `library/<book_rel_path>/_reviews/NN.issues.json`

La ejecucion es 100% conversacional en chat Codex. Esta skill no usa scripts ni CLI.

Definicion de entradas:
- `NN.md`: propuesta inicial del cuento (base de trabajo, no version final).
- `NN.pdf`: seccion/bloque/capitulos oficiales y canonicos base del cuento para contraste de fiabilidad.

## Flujo conversacional obligatorio
1. Descubrir entradas:
   - Buscar `library/_inbox/<inbox_book_title>/NN.md`.
   - Excluir rutas `_ignore`.
   - Emparejar cada `NN.md` con `NN.pdf` por el mismo `NN`.
2. Ejecutar gate canonico antes de avanzar:
   - Si falta `NN.pdf` en cualquier cuento, se bloquea el lote completo.
   - Si no hay senal textual canonica suficiente para contraste de historia en cualquier cuento, se bloquea el lote completo.
   - Paginas no textuales aisladas (portada/mapa) no bloquean por si solas si el conjunto tiene senal narrativa suficiente.
3. Leer y contrastar canon:
   - Usar la skill `pdf` para lectura canonica y evidencia puntual por pagina.
   - No usar OCR ni pipeline parser local en esta skill.
4. Preguntar al usuario con protocolo fijo:
   - Una pregunta por turno con opciones cerradas.
   - Incluir opcion recomendada.
   - Excepcion: si una misma incoherencia se repite en varias ocurrencias, preguntar una sola vez y aplicar en bloque.
5. Construir glosario/contexto en modo `md-first expandido`:
   - Los candidatos salen de `NN.md`.
   - Solo se agregan terminos del PDF cuando desbloquean una incoherencia real detectada en `NN.md`.
   - Preguntar todos los terminos ambiguos detectados, sin recorte por volumen.
6. Generar issues de forma generica:
   - Mantener tipos base obligatorios.
   - Permitir tipos extendidos con justificacion.
   - No hardcodear ejemplos concretos.
7. Escalar decisiones de contexto:
   - Proponer nivel de aplicacion por termino (cuento/libro/ancestros/global).
   - Pedir confirmacion explicita del usuario cuando haya impacto multicuento o multinodo.
8. Escritura incremental durante la conversacion:
   - Escribir directamente en archivos finales, sin carpeta temporal de drafts.
   - `NN.json` en `status: in_review`.
   - Sidecars con estados de trabajo (`pending|confirmed|open`) segun corresponda.
9. Cierre:
   - Consolidar la ronda con salida coherente en `NN.json`, `adaptation_context.json` y `NN.issues.json`.
   - Reportar bloqueos y huecos pendientes para la siguiente ronda si existen.

## Reglas operativas
- Procesa batch de todos los `NN.md` del libro.
- Excluye rutas con `_ignore`.
- Gate canonico obligatorio por lote con bloqueo inmediato ante fallos.
- Contraste canonico:
  - Alineacion semantica `NN.md -> NN.pdf` (no 1:1 por numero de pagina PDF).
  - Issues con `page_number` del cuento adaptado y evidencia de contraste canonico cuando exista.
- Glosario/contexto:
  - `md-first expandido`: base en `NN.md` y ampliacion puntual desde PDF solo para resolver incoherencias reales.
  - Se pregunta termino ambiguo uno a uno con opciones.
  - Contexto jerarquico en nodos: libro + ancestros + global (`library/_reviews/adaptation_context.json`).
  - Escalado a niveles superiores con confirmacion explicita por termino.
- No usar scripts ni contrato CLI en esta skill.
- No introducir reglas especiales basadas en ejemplos concretos del usuario.

## Formato de respuestas
Ver `references/contracts.md`.
