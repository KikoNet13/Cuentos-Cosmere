---
name: notebooklm-comunicacion
description: Skill conversacional para preparar comunicacion con NotebookLM por partes (8+8) y fallback automatico (4+4), generando prompts accionables para _inbox.
---

# NotebookLM Comunicacion

## Objetivo
Estandarizar la comunicacion con NotebookLM para nuevas novelas/sagas:

1. Definir estructura de entrega por cuento en `_inbox` usando partes.
2. Emitir prompts listos para copiar/pegar por archivo.
3. Aplicar fallback automatico `4+4` cuando falle una parte de `8+8`.
4. Entregar mensajes delta para correcciones puntuales sin rehacer el lote completo.

Esta skill es **100% conversacional** y **no usa scripts internos**.

## Scope de la skill

1. Esta skill prepara prompting y operacion de entrega para NotebookLM.
2. No importa cuentos ni mueve archivos al destino final.
3. La fusion/validacion/importacion final pertenece a `ingesta-cuentos`.

## Entradas minimas

1. `book_title` (nombre de carpeta de `_inbox`).
2. Lista de cuentos con:
   - `story_id` (`NN`)
   - `title`
   - `tramo_narrativo_origen`
3. `book_rel_path` opcional (puede definirse despues en `ingesta-cuentos`).

## Estrategia por defecto

1. Cuentos objetivo: 16 paginas.
2. Particion inicial:
   - `NN_a.json` -> paginas `1..8`
   - `NN_b.json` -> paginas `9..16`
3. Si NotebookLM se corta o no devuelve JSON valido:
   - autoescalar para ese bloque a:
     - `NN_a1.json` -> `1..4`
     - `NN_a2.json` -> `5..8`
     - `NN_b1.json` -> `9..12`
     - `NN_b2.json` -> `13..16`

## Flujo operativo

1. Setup de lote
   - Confirmar `book_title`.
   - Confirmar lista de cuentos (`NN`, titulo, tramo).
   - Confirmar si se usa 16 paginas.
2. Emision de prompts por cuento
   - Generar prompt para `NN_a.json`.
   - Generar prompt para `NN_b.json`.
   - Cada prompt pide salida JSON valida y top-level completo.
3. Fallback por error
   - Si falla bloque A o B, emitir prompts de `a1/a2` o `b1/b2` sin preguntar confirmacion adicional.
4. Delta de correccion
   - Si un bloque devuelve JSON valido pero con error de contrato, emitir correccion minima dirigida solo a ese archivo.
5. Handoff
   - Cuando el lote de partes este completo, indicar ejecutar `ingesta-cuentos`.

## Reglas de prompts a NotebookLM

1. Salida: solo JSON valido (sin markdown, sin explicaciones).
2. Top-level obligatorio:
   - `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`
3. `pages` solo en el rango solicitado por archivo.
4. `images.main` obligatorio.
5. `images.secondary` excluido por defecto.
6. Texto en espanol, 50-100 palabras por pagina.

## Plantillas operativas

### A) Prompt base `NN_a.json` (1..8)

```text
PROMPT NOTEBOOKLM - STORY <NN> - PARTE A (PAGINAS 1-8)
Genera SOLO JSON valido.
No uses markdown. No escribas explicaciones.
Devuelve un unico objeto JSON con top-level completo y SOLO 8 paginas (1..8).
Top-level obligatorio exacto:
- story_id
- title
- status
- book_rel_path
- created_at
- updated_at
- cover
- pages
Reglas:
1) story_id="<NN>", title="<TITLE>", status="draft", book_rel_path="<BOOK_REL_PATH_OR_DRAFT>".
2) pages con page_number secuencial 1..8.
3) text en espanol, 50-100 palabras por pagina.
4) Mantener continuidad del tramo narrativo indicado: "<TRAMO>".
5) No inventar campos fuera del contrato.
6) No incluir images.secondary.
Contrato de cover:
- status: "draft"
- prompt: 1-2 frases utiles para ilustracion.
- active_id: ""
- alternatives: []
Contrato de pages[i].images.main:
- status: "draft"
- prompt: 1-2 frases utiles para ilustracion.
- active_id: ""
- alternatives: []
Fechas:
- created_at y updated_at en ISO 8601 UTC.
Salida final:
- SOLO JSON valido.
```

### B) Prompt base `NN_b.json` (9..16)

```text
PROMPT NOTEBOOKLM - STORY <NN> - PARTE B (PAGINAS 9-16)
Genera SOLO JSON valido.
No uses markdown. No escribas explicaciones.
Devuelve un unico objeto JSON con top-level completo y SOLO 8 paginas (9..16).
Top-level obligatorio exacto:
- story_id
- title
- status
- book_rel_path
- created_at
- updated_at
- cover
- pages
Reglas:
1) story_id="<NN>", title="<TITLE>", status="draft", book_rel_path="<BOOK_REL_PATH_OR_DRAFT>".
2) pages con page_number secuencial 9..16.
3) text en espanol, 50-100 palabras por pagina.
4) Mantener continuidad del tramo narrativo indicado: "<TRAMO>".
5) No inventar campos fuera del contrato.
6) No incluir images.secondary.
Contrato de cover:
- status: "draft"
- prompt: 1-2 frases utiles para ilustracion.
- active_id: ""
- alternatives: []
Contrato de pages[i].images.main:
- status: "draft"
- prompt: 1-2 frases utiles para ilustracion.
- active_id: ""
- alternatives: []
Fechas:
- created_at y updated_at en ISO 8601 UTC.
Salida final:
- SOLO JSON valido.
```

### C) Fallback automatico `4+4`

```text
La respuesta se corto o no es JSON valido.
Reentrega SOLO el bloque solicitado con esta particion:
- <NN_a1.json> paginas 1..4
- <NN_a2.json> paginas 5..8
- <NN_b1.json> paginas 9..12
- <NN_b2.json> paginas 13..16
Mantener exactamente el mismo contrato JSON completo.
No usar markdown. No agregar texto fuera del JSON.
```

### D) Delta de correccion por archivo

```text
Correccion de archivo: <NOMBRE_ARCHIVO>
- Problema: <ERROR_CONCRETO>
- Corrige asi: <INSTRUCCION_MINIMA>
- Mantener sin cambios: <CAMPOS_O_BLOQUES_QUE_NO_SE_TOCAN>
Reentrega SOLO ese archivo en JSON valido.
```

## Criterios de salida de la skill

1. Debe quedar claro para el usuario que archivos pedir a NotebookLM.
2. Debe quedar claro cual es el siguiente archivo a generar/corregir.
3. Debe quedar claro cuando pasar a `ingesta-cuentos`.
