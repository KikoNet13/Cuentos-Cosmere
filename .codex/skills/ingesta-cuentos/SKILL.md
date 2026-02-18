---
name: ingesta-cuentos
description: Skill conversacional para fusionar (en memoria) partes NN_a/NN_b, validar, enriquecer reference_ids, importar lotes y generar dossier ChatGPT Project por saga.
---

# Ingesta Cuentos

## Objetivo
Operar como orquestador conversacional entre NotebookLM, ChatGPT Project y la webapp:

1. Recibir en `library/_inbox/<book_title>/` cuentos completos `NN.json` o partes (`NN_a/_b`, `NN_a1/_a2/_b1/_b2`) y `meta.json` opcional.
2. Fusionar partes por cuento en memoria antes de validar (sin crear `NN.json` intermedio en `_inbox`).
3. Validar contrato de cuentos/imagenes/meta.
4. Enriquecer `reference_ids` faltantes antes de importar cuando exista `meta.json`.
5. Bloquear lote completo si hay errores estructurales/editoriales.
6. Importar lote valido a `library/<book_rel_path>/NN.json` con normalizaciones de importacion.
7. Generar/actualizar `library/<book_rel_path>/chatgpt_project_setup.md` con setup y flujo operativo de imagen.
8. Archivar carpeta de inbox procesada en `library/_processed/<book_title>/<timestamp>/` cuando el lote se completa sin pendientes.
9. Emitir mensajes accionables para NotebookLM.

Esta skill es **100% conversacional** y **no usa scripts internos**.

## Flujo obligatorio

1. Descubrimiento de entrada
   - Detectar carpeta `library/_inbox/<book_title>/`.
   - Detectar cuentos por `NN` con prioridad:
     - completo: `NN.json`
     - partes: `NN_a.json` + `NN_b.json`
     - fallback: `NN_a1.json`, `NN_a2.json`, `NN_b1.json`, `NN_b2.json`
   - `meta.json` es opcional.
   - Archivos `.md/.pdf` se ignoran con warning no bloqueante.
   - Parse de entrada robusto: aceptar JSON en UTF-8 y UTF-8 BOM.

2. Pregunta inicial de destino
   - Pedir `book_rel_path` una sola vez por lote.
   - Confirmar slug final antes de importar.

3. Resolucion por cuento (fusion en memoria)
   - Si existe `NN.json` valido, usarlo como fuente canonica del cuento.
   - Si no existe `NN.json`, intentar fusion por combinaciones validas:
     - `a + b`
     - `a1 + a2 + b`
     - `a + b1 + b2`
     - `a1 + a2 + b1 + b2`
   - Validar cada parte como JSON de cuento.
   - Verificar rango de `page_number` por sufijo:
     - `a`: `1..8`
     - `b`: `9..16`
     - `a1`: `1..4`
     - `a2`: `5..8`
     - `b1`: `9..12`
     - `b2`: `13..16`
   - Unir paginas sin duplicados y exigir secuencia final `1..N` sin huecos.
   - Cover final:
     - preferir `a`;
     - si no existe, preferir `a1`;
     - si no, primer bloque valido.
   - Si hay cover distinto entre partes, warning no bloqueante.

4. Validacion estructural de lote
   - Validar todos los cuentos resueltos (completos o fusionados).
   - Si un cuento falla estructura, bloquear lote completo.
   - Entregar errores por cuento con formato accionable para NotebookLM.

5. Enriquecimiento preimport de `reference_ids`
   - Si existe `meta.json` valido del lote, aplicar politica hibrida:
     - respetar `reference_ids` ya presentes;
     - autocompletar slots sin refs en `cover` y `pages[].images.main`.
   - Regla de precedencia:
     - anclas base de estilo (`style_*`) siempre primero;
     - luego anclas semanticas detectadas desde `title`, `text`, `prompt`;
     - eliminar duplicados preservando orden.
   - Politica de cierre:
     - si faltan refs y se pudieron autocompletar, warning no bloqueante;
     - si no hay `meta.json`, no bloquear por refs (warning operativo).

6. Manejo de colisiones
   - Si `library/<book_rel_path>/NN.json` ya existe:
     - preguntar 1 a 1 si se sobrescribe ese cuento;
     - continuar solo con confirmacion explicita.

7. Importacion (solo si lote valido)
   - Forzar `status = definitive`.
   - Rellenar `created_at` si falta.
   - Actualizar `updated_at` siempre.
   - Normalizar `story_id` segun `NN`.
   - Guardar en `library/<book_rel_path>/NN.json`.

8. Meta jerarquico
   - Si existe `_inbox/<book_title>/meta.json`:
     - validar minimos;
     - merge incremental en:
       - `library/<book_rel_path>/meta.json`
       - ancestros de `book_rel_path`
       - `library/meta.json`
   - Si falta `meta.json`: warning no bloqueante.
   - Si hay conflicto semantico real (no tecnico): preguntar al usuario.

9. Dossier ChatGPT Project por saga (obligatorio tras import)
   - Generar o regenerar siempre:
     - `library/<book_rel_path>/chatgpt_project_setup.md`
   - Fuente para derivacion:
     - `library/<book_rel_path>/meta.json` (anclas, reglas);
     - `library/<book_rel_path>/NN.json` (prompts/slots por cuento y pagina).
   - Contenido minimo del dossier:
     - nombre sugerido del project;
     - instrucciones maestras de continuidad visual;
     - checklist obligatorio de fase de anclas antes de paginas;
     - flujo rapido por slot de portada y pagina (copiar prompt + refs, generar, pegar y guardar);
     - politica de QA rapido (coherencia de personajes, paleta, encuadre, continuidad);
     - troubleshooting de portapapeles/navegador.

10. Archivado de inbox
   - Si el lote fue importado completo y no hay pendientes/placeholders:
     - mover `library/_inbox/<book_title>/` a `library/_processed/<book_title>/<timestamp>/`.
   - Si hay pendientes:
     - no mover carpeta;
     - reportar exactamente que `NN`/parte falta o esta invalida.

11. Resumen de cierre
   - Informar:
     - cuentos importados,
     - warnings,
     - colisiones resueltas,
     - estado de fusion por cuento,
     - cobertura de enriquecimiento de refs por cuento/pagina,
     - estado de dossier (`generado`/`actualizado`),
     - estado de archivado (`_processed` o pendiente),
     - mensajes para NotebookLM (si hubo bloqueos).

## Reglas de validacion del cuento resuelto (`NN`)

1. Top-level obligatorio:
   - `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
2. `story_id`:
   - si no coincide con `NN`, autocorregir a `NN`.
3. `pages`:
   - lista no vacia;
   - `page_number` secuencial `1..N` sin huecos;
   - `text` string;
   - `images.main` obligatorio.
4. Contrato de slot (`cover`, `images.main`, `images.secondary`):
   - `status`, `prompt` (string), `active_id`, `alternatives[]`;
   - `reference_ids[]` opcional.
5. Contrato de alternativa:
   - `id` (filename con extension),
   - `slug`,
   - `asset_rel_path`,
   - `mime_type`,
   - `status`,
   - `created_at`,
   - `notes`.

## Reglas de validacion de partes (`NN_a/_b/...`)

1. Nombre permitido:
   - `NN_a.json`, `NN_b.json`, `NN_a1.json`, `NN_a2.json`, `NN_b1.json`, `NN_b2.json`.
2. Cada parte debe parsear como JSON valido de cuento (top-level completo).
3. Parse aceptado para UTF-8 y UTF-8 BOM.
4. `pages[].page_number` debe caer en su rango esperado por sufijo.
5. Si parte contiene texto plano placeholder/no JSON:
   - error bloqueante `input.pending_notebooklm`.

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
5. Operativo recomendado para salida lista de imagen:
   - categorias de anchors con prefijos `style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`.

## Reglas de enriquecimiento de referencias

1. Slot objetivo:
   - `cover`
   - `pages[].images.main`
2. Exclusion:
   - slots con `status = not_required`.
3. Politica:
   - respetar refs existentes;
   - autocompletar solo faltantes.
4. Fuente de truth para refs:
   - filenames de `meta.anchors[].image_filenames[]`.
5. No permitido en refs:
   - IDs opacos de alternatives (`<uuid>_<slug>.<ext>`) salvo que coincidan explicitamente como anchor filename.

## Modo refresh manual del dossier (sin reimportar)

Usar este modo cuando ya existe `library/<book_rel_path>/` y solo se quiere refrescar el setup de ChatGPT Project.

1. No leer `_inbox` ni mover `_processed`.
2. Cargar `library/<book_rel_path>/meta.json` y todos los `NN.json` del libro.
3. Regenerar `library/<book_rel_path>/chatgpt_project_setup.md`.
4. Reportar:
   - fecha de actualizacion,
   - total de cuentos detectados,
   - total de anchors y reglas aplicadas,
   - warnings (si falta `meta.json` o hay refs sin resolver).

## Formato de respuesta en chat

1. Si el lote es invalido:
   - no mover nada;
   - responder con bloques por cuento:
     - `NN` afectado y/o parte (`NN_a`, `NN_b`, ...),
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

Recomendado para flujo listo de imagen:
- meta.json con collection.title, anchors[], style_rules, continuity_rules, updated_at.
- reference_ids apuntando a anchors[].image_filenames.

No entregues .md ni .pdf para ingesta.
```

### A2) Fallback de particion para NotebookLM (`4+4`)

```text
Se corto la respuesta de NotebookLM. Reentrega este cuento por bloques:
- NN_a1.json paginas 1..4
- NN_a2.json paginas 5..8
- NN_b1.json paginas 9..12
- NN_b2.json paginas 13..16

Mantener mismo contrato JSON completo en cada parte.
No usar markdown, no agregar texto fuera del JSON.
```

### B) Mensaje inicial para ChatGPT Project (setup)

```text
Voy a pasarte prompts desde NN.json/meta.json.
Genera imagenes manteniendo continuidad visual estable.
Cuando termines cada imagen, devuelveme archivo con nombre opaco exacto <uuid>_<slug>.<ext>.
No cambies IDs ni nombres de archivos.
```

### B2) Plantilla de `chatgpt_project_setup.md` por saga

Plantilla reusable en: `references/chatgpt_project_setup_template.md`.

```md
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

## Fase 1 obligatoria - anclas
1. Generar primero anclas de `meta.json` (especialmente `style_*`, `char_*`, `env_*`, `prop_*`, `cover_*`).
2. Validar continuidad base antes de producir paginas.
3. Registrar variantes utiles como alternativas del propio anchor.

## Fase 2 - portada y paginas
1. Abrir editor de portada: `/<book>/<NN>?editor=1`.
2. Para cada slot (cover/main/secondary):
   - copiar prompt;
   - copiar refs individuales;
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
Plantilla de dossier: `references/chatgpt_project_setup_template.md`.
