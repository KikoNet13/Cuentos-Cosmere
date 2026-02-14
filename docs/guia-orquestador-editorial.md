# Guía de uso del orquestador editorial

Esta guía describe el flujo completo para pasar propuestas `NN.md` de `library/_inbox/` a cuentos canónicos `NN.json` mediante revisión conversacional por severidad.

## Objetivo del pipeline

Aplicar una cadena de filtros editoriales con trazabilidad total:

1. Contexto canónico jerárquico.
2. Ingesta técnica a JSON.
3. Etapa texto por severidad.
4. Etapa prompts por severidad.
5. Cierre por gates de criticidad.

## Precondiciones

1. Propuestas en `library/_inbox/<titulo-libro>/`.
2. Cuentos en formato `NN.md` (dos dígitos).
3. Referencia canónica en PDF dentro del inbox del libro.
4. Carpeta `_ignore` para excluir fuentes de ingesta.
5. Ruta de destino definida como `book_rel_path` (por ejemplo: `cosmere/nacidos-de-la-bruma-era-1/el-imperio-final`).

## Skills y propósito (sin comandos embebidos)

1. `revision-contexto-canon`
   - Construye `context_chain.json` y `glossary_merged.json`.
   - Opcional: revisión ligera no bloqueante de terminología con `context_review.json`.
2. `revision-texto-deteccion`
   - Detecta hallazgos en `text.current` para una banda de severidad.
3. `revision-texto-decision-interactiva`
   - Aplica decisiones por hallazgo de texto (`accepted|rejected|defer`).
4. `revision-texto-contraste-canon`
   - Contrasta texto adaptado frente a canon PDF + glosario.
5. `revision-prompts-deteccion`
   - Detecta hallazgos en prompts para una banda de severidad.
6. `revision-prompts-decision-interactiva`
   - Aplica decisiones por hallazgo de prompts.
7. `revision-prompts-contraste-canon`
   - Contrasta prompts frente a canon y continuidad visual.
8. `revision-orquestador-editorial`
   - Ejecuta todo el flujo por libro, con pasadas automáticas y gates.

## Cascada por severidad

Orden fijo:

1. `critical`
2. `major`
3. `minor`
4. `info`

Topes por severidad:

- `critical`: 5 pasadas
- `major`: 4 pasadas
- `minor`: 3 pasadas
- `info`: 2 pasadas

Reglas:

- `critical|major` deben converger para cerrar etapa.
- `minor|info` no bloquean cierre global si quedan explícitamente decididos.
- Si texto no converge en `critical|major`, prompts no se ejecuta.

## Ciclo conversacional por severidad

Para cada banda activa:

1. Detección
   - genera `NN.findings.json`
   - devuelve hallazgos priorizados por página y categoría.
2. Decisión interactiva
   - persiste decisiones en `NN.choices.json`
   - aplica cambios aceptados sobre campos `current`.
3. Contraste canónico
   - genera `NN.contrast.json`
   - si hay alertas abiertas del nivel activo, se repite pasada.

Histórico de pasadas:

- `NN.passes.json`

## Sidecars

Ubicación:

- `library/<book_rel_path>/_reviews/`

Archivos:

- `context_chain.json`
- `glossary_merged.json`
- `context_review.json` (manual, no bloqueante)
- `pipeline_state.json`
- `NN.findings.json`
- `NN.choices.json`
- `NN.contrast.json`
- `NN.passes.json`
- derivados opcionales para UI/editor:
  - `NN.review.json`
  - `NN.review.md`
  - `NN.decisions.json`

## Flujo interactivo final

1. El usuario elige libro destino.
2. El agente construye contexto y confirma inventario.
   - Si existe `context_review.json`, se aplica al glosario efectivo.
   - La revisión ligera se dispara solo desde `revision-contexto-canon`, no automáticamente en el orquestador.
3. Por cada banda:
   - presenta incoherencias
   - propone opciones
   - recoge decisiones
   - contrasta contra canon.
4. Repite pasadas hasta converger o bloquear.
5. Ejecuta prompts solo tras convergencia de texto en `critical|major`.
6. Cierra con estado final por cuento (`ready`, `text_blocked`, `prompt_blocked`).

## UI lectura/editor

1. Lectura (por defecto): `/story/<ruta>?p=N`
2. Editorial: `/story/<ruta>?p=N&editor=1`

La UI editorial es para ajustes puntuales; el flujo de revisión integral se realiza por skills conversacionales.
