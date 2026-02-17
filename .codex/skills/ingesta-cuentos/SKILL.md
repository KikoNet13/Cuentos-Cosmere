---
name: ingesta-cuentos
description: Skill conversacional para validar e importar lotes NN.json/meta.json desde library/_inbox al contrato final de library/, con mensajes accionables para NotebookLM y soporte de flujo 3 IAs.
---

# Ingesta Cuentos

## Objetivo
Operar como orquestador conversacional entre NotebookLM, ChatGPT Project y la webapp:

1. Recibir en `library/_inbox/<book_title>/` archivos `NN.json` (obligatorio) y `meta.json` (opcional).
2. Validar contrato nuevo de cuentos e imagenes.
3. Bloquear lote completo si hay errores de contrato editorial/estructural.
4. Mover lote valido a `library/<book_rel_path>/` con normalizaciones de importacion.
5. Emitir mensajes accionables listos para copiar en NotebookLM.

Esta skill es **100% conversacional** y **no usa scripts internos**.

## Flujo obligatorio

1. Descubrimiento de entrada
   - Detectar carpeta `library/_inbox/<book_title>/`.
   - Incluir solo `NN.json` (dos digitos).
   - `meta.json` es opcional.
   - Archivos `.md/.pdf` se ignoran con warning no bloqueante.

2. Pregunta inicial de destino
   - Pedir `book_rel_path` una sola vez por lote.
   - Confirmar slug final antes de mover archivos.

3. Validacion de lote
   - Validar todos los `NN.json` del lote.
   - Si un cuento falla, bloquear lote completo.
   - Entregar errores por cuento con formato accionable para NotebookLM.

4. Manejo de colisiones
   - Si `library/<book_rel_path>/NN.json` ya existe:
     - preguntar 1 a 1 si se sobrescribe ese cuento;
     - continuar solo con confirmacion explicita.

5. Importacion (solo si lote valido)
   - Forzar `status = definitive`.
   - Rellenar `created_at` si falta.
   - Actualizar `updated_at` siempre.
   - Normalizar `story_id` segun nombre de archivo (`NN`).
   - Guardar en `library/<book_rel_path>/NN.json`.

6. Meta jerarquico
   - Si existe `_inbox/<book_title>/meta.json`:
     - validar minimos;
     - merge incremental en:
       - `library/<book_rel_path>/meta.json`
       - ancestros de `book_rel_path`
       - `library/meta.json`
   - Si falta `meta.json`: warning no bloqueante.
   - Si hay conflicto semantico real (no tecnico): preguntar al usuario.

7. Resumen de cierre
   - Informar:
     - cuentos importados,
     - warnings,
     - colisiones resueltas,
     - mensajes para NotebookLM (si hubo bloqueos).

## Reglas de validacion de `NN.json`

1. Nombre de archivo: `NN.json`.
2. Top-level obligatorio:
   - `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
3. `story_id`:
   - si no coincide con `NN`, autocorregir a `NN`.
4. `pages`:
   - lista no vacia;
   - `page_number` secuencial `1..N` sin huecos;
   - `text` string;
   - `images.main` obligatorio.
5. Contrato de slot (`cover`, `images.main`, `images.secondary`):
   - `status`, `prompt` (string), `active_id`, `alternatives[]`;
   - `reference_ids[]` opcional.
6. Contrato de alternativa:
   - `id` (filename con extension),
   - `slug`,
   - `asset_rel_path`,
   - `mime_type`,
   - `status`,
   - `created_at`,
   - `notes`.

## Reglas de validacion de `meta.json`

1. Minimos:
   - `collection.title`,
   - `anchors[]`,
   - `updated_at`.
2. Anchor minimo:
   - `id`, `name`, `prompt`, `image_filenames[]`.
3. Anchor ampliado permitido:
   - `status`, `active_id`, `alternatives[]`.
4. Campos opcionales permitidos:
   - `style_rules`,
   - `continuity_rules`.

## Formato de respuesta en chat

1. Si el lote es invalido:
   - no mover nada;
   - responder con bloques por cuento:
     - `NN` afectado,
     - error concreto,
     - correccion sugerida para NotebookLM.

2. Si el lote es valido:
   - confirmar destino,
   - listar importaciones,
   - listar warnings no bloqueantes.

3. Si hay colision:
   - preguntar 1 a 1:
     - opcion 1: sobrescribir,
     - opcion 2: mantener existente y omitir ese `NN`.

## Plantillas operativas

### A) Mensaje inicial para NotebookLM (setup)

Usa esta plantilla al arrancar un libro nuevo:

```text
Genera un lote de cuentos en JSON para ingesta automatica.
Destino de entrega: library/_inbox/<BOOK_TITLE>/

Formato requerido por cuento: NN.json (dos digitos)
- story_id, title, status, book_rel_path, created_at, updated_at, cover, pages
- pages[] con page_number secuencial 1..N
- text como string
- images.main obligatorio (slot completo)
- images.secondary opcional
- slot: status, prompt, active_id, alternatives[], reference_ids[] opcional
- alternativa: id(filename), slug, asset_rel_path, mime_type, status, created_at, notes

Opcional: meta.json con collection.title, anchors[], updated_at.
No entregues .md ni .pdf para ingesta.
```

### B) Mensaje inicial para ChatGPT Project (setup)

```text
Voy a pasarte prompts desde NN.json/meta.json.
Genera imagenes manteniendo continuidad visual estable.
Cuando termines cada imagen, devuelveme archivo con nombre opaco exacto <uuid>_<slug>.<ext>.
No cambies IDs ni nombres de archivos.
```

### C) Delta update para NotebookLM (correcciones)

```text
Correcciones de lote para reentrega:
<LISTA_DE_ERRORES_POR_NN>

Reentrega solo los NN afectados en library/_inbox/<BOOK_TITLE>/.
Mantener el resto sin cambios.
```

## Referencia
Contrato completo: `references/contracts.md`.
