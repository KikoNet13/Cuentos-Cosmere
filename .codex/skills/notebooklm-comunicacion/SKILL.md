---
name: notebooklm-comunicacion
description: Skill conversacional para preparar comunicacion con NotebookLM en 4 fases: plan de coleccion, meta/anclas, partes de cuentos y deltas de correccion.
---

# NotebookLM Comunicacion

## Objetivo
Estandarizar la comunicacion con NotebookLM para nuevas novelas/sagas:

1. Definir plan editorial de coleccion (lista de cuentos y tramos).
2. Obtener `meta.json` de libro con anclas, reglas de estilo y continuidad.
3. Emitir prompts listos para entrega de cuentos por partes (`8+8`) y fallback (`4+4`).
4. Emitir mensajes delta por archivo para corregir errores sin rehacer el lote.
5. Forzar prompts largos en espanol estructurado para `cover` y `pages[].images.main`.

Esta skill es **100% conversacional** y **no usa scripts internos**.

## Scope de la skill

1. Prepara prompting y operacion de entrega para NotebookLM.
2. No importa cuentos ni mueve archivos al destino final.
3. La fusion/validacion/importacion final pertenece a `ingesta-cuentos`.

## Entradas minimas

1. `book_title` (nombre de carpeta de `_inbox`).
2. Fuente canonica cargada en NotebookLM (novela/saga origen).
3. Lista de cuentos objetivo (si no existe, pedirla en fase de plan).
4. `book_rel_path` opcional (puede confirmarse despues en `ingesta-cuentos`).

## Convencion de anclas y referencias

1. IDs de ancla por categoria reusable:
   - `style_*`
   - `char_*`
   - `env_*`
   - `prop_*`
   - `cover_*`
2. Cada saga define anclas narrativas propias (personajes/escenas/objetos).
3. `reference_ids` de slots debe apuntar a filenames declarados en `meta.anchors[].image_filenames[]`.
4. No usar `uuid_slug` de assets finales dentro de `reference_ids`.

## Estandar de prompt de slot (obligatorio)

Aplica a `cover.prompt` y `pages[].images.main.prompt`.

1. Idioma canonico: espanol estructurado.
2. Estructura fija de 8 bloques con este orden exacto:
   - `OBJETIVO DE ILUSTRACION`
   - `CONTINUIDAD VISUAL OBLIGATORIA`
   - `COMPOSICION Y ENCUADRE`
   - `PERSONAJES Y ACCION`
   - `ENTORNO, PALETA E ILUMINACION`
   - `REFERENCIAS (reference_ids)`
   - `RESTRICCIONES / NEGATIVOS`
   - `FORMATO DE SALIDA`
3. Perfil balanceado de longitud:
   - `cover.prompt`: 900-1700 caracteres.
   - `pages[].images.main.prompt`: 700-1500 caracteres.
4. Excepcion:
   - si `status = not_required`, se permite prompt corto descriptivo.

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

## Flujo oficial (4 fases)

1. Plan de coleccion
   - pedir listado de cuentos (`story_id`, `title`, `tramo_narrativo_origen`, `paginas_objetivo`).
2. Meta/anclas
   - pedir `meta.json` del libro con `collection`, `anchors`, `style_rules`, `continuity_rules`, `updated_at`.
3. Cuentos por partes
   - pedir `NN_a.json` y `NN_b.json` (o fallback `a1/a2/b1/b2`) con contrato completo.
4. Deltas
   - corregir solo archivos afectados por: JSON truncado, JSON invalido, rango incorrecto, faltantes de `reference_ids` o prompts fuera de estandar.

## Reglas de prompts a NotebookLM

1. Salida: solo JSON valido (sin markdown, sin explicaciones).
2. Contrato de cuento top-level obligatorio:
   - `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
3. `pages` solo en el rango solicitado por archivo.
4. `images.main` obligatorio.
5. `images.secondary` excluido por defecto.
6. Texto narrativo en espanol, 50-100 palabras por pagina.
7. Si existe `meta.json`, incluir `reference_ids` cuando sea posible usando `anchors[].image_filenames`.
8. Prompts de slot en espanol estructurado con el estandar de 8 bloques.
9. Respetar perfil balanceado de longitud por slot.

## Plantillas operativas

### A) Prompt de plan de coleccion

```text
PROMPT NOTEBOOKLM - PLAN DE COLECCION
Devuelve SOLO JSON valido.
No uses markdown ni explicaciones.

Objetivo:
- Dividir la obra canonica en cuentos ilustrados de 16 paginas.
- Mantener continuidad narrativa y cortes en hitos claros.

Salida exacta:
{
  "collection_title": "<BOOK_TITLE>",
  "stories": [
    {
      "story_id": "01",
      "title": "...",
      "tramo_narrativo_origen": "...",
      "paginas_objetivo": 16
    }
  ]
}

Reglas:
1) `story_id` en 2 digitos y secuencial.
2) `paginas_objetivo` fijo en 16.
3) Cubrir toda la obra sin solapamientos ilogicos.
4) SOLO JSON valido.
```

### B) Prompt de `meta.json` (anclas + reglas)

```text
PROMPT NOTEBOOKLM - META JSON DE LIBRO
Devuelve SOLO JSON valido.
No uses markdown ni explicaciones.

Genera `meta.json` para la coleccion "<BOOK_TITLE>" con este top-level exacto:
- collection
- anchors
- style_rules
- continuity_rules
- updated_at

Reglas obligatorias:
1) collection.title = "<BOOK_TITLE>".
2) anchors[] debe incluir categorias:
   - style_* (minimo 2)
   - cover_* (minimo 1)
   - char_* (personajes principales)
   - env_* (escenarios recurrentes)
   - prop_* (objetos simbolicos)
3) Cada anchor con:
   - id
   - name
   - prompt
   - image_filenames (array de filenames placeholder .png o .jpg)
4) `style_rules` y `continuity_rules` deben ser arrays de reglas claras y accionables.
5) `updated_at` en ISO 8601 UTC.
6) SOLO JSON valido.

Ejemplo de anchor:
{
  "id": "char_katniss_base",
  "name": "Katniss base",
  "prompt": "Modelo consistente de personaje...",
  "image_filenames": ["anchor_char_katniss_base_v1.png"]
}
```

### C) Prompt base `NN_a.json` (1..8)

```text
PROMPT NOTEBOOKLM - STORY <NN> - PARTE A (PAGINAS 1-8)
Genera SOLO JSON valido.
No uses markdown. No escribas explicaciones.

Devuelve un unico objeto JSON con top-level completo y SOLO paginas 1..8.
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
7) Si `meta.json` existe, incluye `reference_ids` usando SOLO filenames de `anchors[].image_filenames`.
8) `cover.prompt` y `pages[].images.main.prompt` deben seguir la estructura fija de 8 bloques y longitudes balanceadas.

Contrato de cover:
- status: "draft"
- prompt: espanol estructurado en 8 bloques, 900-1700 caracteres
- reference_ids: [] o lista de filenames de anchors
- active_id: ""
- alternatives: []

Contrato de pages[i].images.main:
- status: "draft"
- prompt: espanol estructurado en 8 bloques, 700-1500 caracteres
- reference_ids: [] o lista de filenames de anchors
- active_id: ""
- alternatives: []

Fechas:
- created_at y updated_at en ISO 8601 UTC.

Salida final:
- SOLO JSON valido.
```

### D) Prompt base `NN_b.json` (9..16)

```text
PROMPT NOTEBOOKLM - STORY <NN> - PARTE B (PAGINAS 9-16)
Genera SOLO JSON valido.
No uses markdown. No escribas explicaciones.

Devuelve un unico objeto JSON con top-level completo y SOLO paginas 9..16.
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
7) Si `meta.json` existe, incluye `reference_ids` usando SOLO filenames de `anchors[].image_filenames`.
8) `cover.prompt` y `pages[].images.main.prompt` deben seguir la estructura fija de 8 bloques y longitudes balanceadas.

Contrato de cover:
- status: "draft"
- prompt: espanol estructurado en 8 bloques, 900-1700 caracteres
- reference_ids: [] o lista de filenames de anchors
- active_id: ""
- alternatives: []

Contrato de pages[i].images.main:
- status: "draft"
- prompt: espanol estructurado en 8 bloques, 700-1500 caracteres
- reference_ids: [] o lista de filenames de anchors
- active_id: ""
- alternatives: []

Fechas:
- created_at y updated_at en ISO 8601 UTC.

Salida final:
- SOLO JSON valido.
```

### E) Fallback automatico `4+4`

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

### F) Delta de correccion por archivo

```text
Correccion de archivo: <NOMBRE_ARCHIVO>
- Problema: <ERROR_CONCRETO>
- Corrige asi: <INSTRUCCION_MINIMA>
- Mantener sin cambios: <CAMPOS_O_BLOQUES_QUE_NO_SE_TOCAN>
Reentrega SOLO ese archivo en JSON valido.
```

### G) Deltas especializados

```text
[<NOMBRE_ARCHIVO>] contract.invalid_json
- Problema: JSON truncado o invalido.
- Corrige asi: reentrega el archivo completo, solo JSON valido.

[<NOMBRE_ARCHIVO>] merge.invalid_part_range
- Problema: page_number fuera del rango esperado por el sufijo del archivo.
- Corrige asi: ajusta pages al rango correcto y reentrega solo ese archivo.

[<NOMBRE_ARCHIVO>] refs.missing_reference_ids
- Problema: faltan reference_ids en cover o pages.images.main.
- Corrige asi: agrega reference_ids con filenames existentes en meta.anchors[].image_filenames.

[<NOMBRE_ARCHIVO>] prompts.too_short
- Problema: prompt fuera del minimo de longitud del perfil balanceado.
- Corrige asi: reescribe el prompt con los 8 bloques y longitud valida.

[<NOMBRE_ARCHIVO>] prompts.missing_sections
- Problema: faltan uno o mas encabezados obligatorios en el prompt.
- Corrige asi: reentrega prompt con los 8 bloques en orden exacto.

[<NOMBRE_ARCHIVO>] prompts.language_mismatch
- Problema: prompt en idioma no canonico o mezcla excesiva.
- Corrige asi: reescribe el prompt completo en espanol estructurado.

[<NOMBRE_ARCHIVO>] prompts.range_incomplete
- Problema: parte entregada con prompts validos solo en una parte de paginas del rango.
- Corrige asi: reentrega el archivo completo con prompts validos en todas las paginas del rango.
```

### H) Reentrega prompts-only para cuentos existentes

```text
PROMPT NOTEBOOKLM - REENTREGA PROMPTS-ONLY STORY <NN>
Genera SOLO JSON valido.
No uses markdown. No escribas explicaciones.

Objetivo:
- Reescribir UNICAMENTE prompts de portada y pages.main al estandar largo balanceado en espanol.

Mantener SIN CAMBIOS:
- story_id
- title
- status
- book_rel_path
- created_at
- text (todas las paginas)
- reference_ids (cover y pages.main)
- active_id (cover y pages.main)
- alternatives (cover y pages.main)
- page_number

Cambiar SOLO:
- cover.prompt
- pages[].images.main.prompt
- updated_at

Reglas de prompt:
1) 8 bloques obligatorios en orden exacto.
2) cover: 900-1700 caracteres.
3) pages.main: 700-1500 caracteres.
4) Espanaol estructurado.
5) Si un slot tiene status `not_required`, se permite prompt corto.

Salida final:
- SOLO JSON valido del cuento completo `NN.json`.
```

## Criterios de salida de la skill

1. Debe quedar claro en cada paso que archivo pedir a NotebookLM.
2. Debe quedar claro el siguiente archivo a generar/corregir.
3. Debe quedar claro cuando pasar a `ingesta-cuentos`.
4. El usuario debe terminar con:
   - `meta.json` valido del libro,
   - partes `NN_a/NN_b` (o fallback) por cuento,
   - contrato listo para fusion/importacion.
