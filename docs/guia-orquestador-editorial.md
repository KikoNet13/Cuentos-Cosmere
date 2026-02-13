# Guía de uso del orquestador editorial

Esta guía describe el flujo completo para pasar propuestas `NN.md` de `library/_inbox/` a cuentos canónicos `NN.json` con cascada por severidad.

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
5. Ruta de destino definida como `book_rel_path` (por ejemplo `cosmere/nacidos-de-la-bruma-era-1/el-imperio-final`).

## Skills y propósito

1. `revision-contexto-canon`
   - Construye `context_chain.json` y `glossary_merged.json`.
2. `revision-texto-deteccion`
   - Detecta findings en `text.current` para una banda de severidad.
3. `revision-texto-decision-interactiva`
   - Aplica decisiones por finding (`accepted|rejected|defer`) sobre texto.
4. `revision-texto-contraste-canon`
   - Contrasta texto adaptado frente a canon PDF + glosario.
5. `revision-prompts-deteccion`
   - Detecta findings en prompts para una banda de severidad.
6. `revision-prompts-decision-interactiva`
   - Aplica decisiones por finding sobre prompts.
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

## Ciclo de 3 skills por severidad

Para cada banda activa se ejecuta:

1. Detección
   - genera `NN.findings.json`.
2. Decisión interactiva
   - persiste decisiones en `NN.choices.json`
   - aplica cambios aceptados sobre campos `current`.
3. Contraste canon
   - genera `NN.contrast.json`
   - si hay alertas abiertas del nivel activo, reinyecta otra pasada.

Histórico de pasadas:

- `NN.passes.json`

## Sidecars

Ubicación:

- `library/<book_rel_path>/_reviews/`

Archivos:

- `context_chain.json`
- `glossary_merged.json`
- `pipeline_state.json`
- `NN.findings.json`
- `NN.choices.json`
- `NN.contrast.json`
- `NN.passes.json`
- derivados opcionales para UI/editor:
  - `NN.review.json`
  - `NN.review.md`
  - `NN.decisions.json`

## Ejecución por skill (manual)

## 1) Contexto

```powershell
python -c "from app.editorial_orquestador import run_contexto_canon; r=run_contexto_canon(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final'); print(r['context_chain_rel']); print(r['glossary_merged_rel'])"
```

## 2) Detección de texto (ejemplo `critical`)

```powershell
python -c "from app.editorial_orquestador import run_text_detection; r=run_text_detection(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final', story_id='01', severity_band='critical', pass_index=1); print(r['findings_json_rel']); print(r['findings'], r['alerts_open'])"
```

## 3) Decisión de texto

```powershell
python -c "from app.editorial_orquestador import run_text_decision_interactiva; r=run_text_decision_interactiva(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final', story_id='01', severity_band='critical', pass_index=1); print(r['choices_json_rel']); print(r['applied_changes'], r['alerts_open'])"
```

## 4) Contraste de texto

```powershell
python -c "from app.editorial_orquestador import run_text_contrast_canon; r=run_text_contrast_canon(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final', story_id='01', severity_band='critical'); print(r['contrast_json_rel']); print(r['alerts'])"
```

## 5) Orquestación completa

```powershell
python -c "from app.editorial_orquestador import run_orquestador_editorial; r=run_orquestador_editorial(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final'); print(r['phase']); print(r['pipeline_state_rel'])"
```

## UI lectura/editor

1. Lectura (por defecto):
   - `/story/<ruta>?p=N`
2. Editorial:
   - `/story/<ruta>?p=N&editor=1`

En lectura no se muestran formularios editoriales; en editorial sí se muestran comparativas y controles.
