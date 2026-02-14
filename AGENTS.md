# AGENTS

## Propósito

Este repositorio aplica un flujo profesional para el **Generador de cuentos ilustrados**.

## Reglas operativas

1. No ejecutar comandos persistentes sin petición explícita del usuario.
2. `runserver` está prohibido por defecto en tareas de validación.
3. Preferir comandos finitos (`--help`, validaciones acotadas, timeouts).
4. Evitar acciones destructivas fuera del alcance de la tarea activa.
5. Tras cada plan aprobado: registrar tarea, actualizar índice/changelog, cerrar con un commit único y hacer push a GitHub.

## Contrato de datos vigente

1. Fuente de verdad: `library/`.
2. Un libro se detecta por presencia de uno o más archivos `NN.json` en su carpeta.
3. Cada cuento se guarda en un único archivo `NN.json` (2 dígitos).
4. Estructura canónica de `NN.json`:
   - top-level: `schema_version`, `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `pages`.
   - por página: `page_number`, `status`, `text.original`, `text.current`, `images`.
   - `images.main` obligatorio, `images.secondary` opcional.
5. Cada slot de imagen define `status`, `prompt.original`, `prompt.current`, `active_id` y `alternatives[]`.
6. Cada alternativa define `id`, `slug`, `asset_rel_path`, `mime_type`, `status`, `created_at`, `notes`.
7. Los assets de imagen se nombran con formato opaco `img_<uuid>_<slug>.<ext>` y la relación página/slot vive en JSON.
8. `library/_inbox/` se usa como bandeja de propuestas editoriales `.md` y referencias `.pdf`.
9. `library/_backups/` es opcional para respaldos manuales.
10. Sidecars de revisión en `library/<book>/_reviews/`:
    - `context_chain.json`
    - `glossary_merged.json`
    - `context_review.json`
    - `pipeline_state.json`
    - `NN.findings.json`
    - `NN.choices.json`
    - `NN.contrast.json`
    - `NN.passes.json`
    - derivados opcionales para UI: `NN.review.json|md`, `NN.decisions.json`.
11. Ciclo de estado de cuento:
    - `draft`
    - `text_reviewed` o `text_blocked`
    - `prompt_reviewed` o `prompt_blocked`
    - `ready`

## Flujo editorial oficial

1. Flujo principal: skill `revision-orquestador-editorial`.
2. El orquestador ejecuta contexto + ingesta + cascada por severidad.
3. Orden de severidad por etapa: `critical -> major -> minor -> info`.
4. Cada severidad ejecuta ciclo de 3 skills:
   - detección
   - decisión interactiva
   - contraste con canon.
5. Etapa texto primero; etapa prompts solo si texto converge en `critical|major`.
6. Topes por severidad:
   - `critical`: 5
   - `major`: 4
   - `minor`: 3
   - `info`: 2
7. Gate:
   - `critical|major` sin convergencia bloquea cuento y detiene libro.
   - `minor|info` no bloquean si quedan aceptados/rechazados/defer con nota.

## Skills editoriales (modo conversacional)

1. `revision-contexto-canon`
2. `revision-texto-deteccion`
3. `revision-texto-decision-interactiva`
4. `revision-texto-contraste-canon`
5. `revision-prompts-deteccion`
6. `revision-prompts-decision-interactiva`
7. `revision-prompts-contraste-canon`
8. `revision-orquestador-editorial`

Regla: las skills son de agente y se usan en diálogo interactivo, sin comandos hardcodeados.

## Runtime de app

1. La webapp lee `NN.json` directo desde disco.
2. No se usa SQLite para navegación ni lectura.
3. Modo lectura por defecto: `/story/<path>?p=N`.
4. Modo editorial: `/story/<path>?p=N&editor=1`.

## CLI vigente

1. `python manage.py runserver`
2. No existen comandos CLI de ingesta en el flujo oficial.

## Sistema documental

1. Operación principal en este archivo (`AGENTS.md`).
2. ADR en `docs/adr/` para decisiones arquitectónicas.
3. Tareas en `docs/tasks/` con índice en `docs/tasks/INDICE.md`.
4. `CHANGELOG.md` breve, siempre enlazando a la tarea correspondiente.

## Convención de tareas

1. Formato: `TAREA-001-<slug>`.
2. Numeración global continua del repositorio.
3. Fecha documental: `dd/mm/aa HH:MM`.
4. Mensaje de commit: `Tarea 001: <resumen>`.

## Flujo Git

1. Rama única: `main`.
2. Un commit por tarea planificada.
3. No usar ramas funcionales salvo necesidad explícita.

## Cierre de tarea

Una tarea queda cerrada cuando:

1. El alcance pactado está implementado.
2. Se ejecutaron validaciones finitas reproducibles.
3. Se actualizaron archivo de tarea, índice y changelog breve.
4. Se creó el commit final de la tarea.
