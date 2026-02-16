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
10. Sidecars de revisión vigentes en `library/<book>/_reviews/`:
    - `NN.review.json` (maestro por cuento)
    - `NN.decisions.log.jsonl` (log final por hallazgo resuelto)
11. Sidecars legacy (`context_chain`, `glossary_merged`, `pipeline_state`, `NN.findings`, etc.) quedan fuera de contrato y se eliminan al ejecutar el nuevo flujo.
12. Ciclo de estado de cuento:
    - `draft`
    - `in_review`
    - `definitive`

## Flujo editorial oficial

1. Flujo principal: skill `adaptacion-orquestador`.
2. `target_age` es obligatorio al iniciar.
3. Secuencia fija:
   - contexto
   - texto
   - prompts
   - cierre
4. Orden de severidad por etapa:
   - `critical -> major -> minor -> info`
5. Las decisiones se resuelven por bloques de severidad.
6. Cada hallazgo ofrece 1-3 propuestas IA y opción humana libre `D`.
7. Texto siempre antes de prompts.
8. Gate visual de cierre: `prompt.main`.
9. Cierre solo si `open_counts` queda en cero para todas las severidades.

## Skills editoriales (modo conversacional)

1. `adaptacion-contexto`
2. `adaptacion-texto`
3. `adaptacion-prompts`
4. `adaptacion-cierre`
5. `adaptacion-orquestador`

Reglas:
- Las skills se usan en diálogo interactivo.
- Si una skill necesita ejecutar lógica, el script vive dentro de esa skill (`<skill>/scripts/...`).
- `app/` no ejecuta pipeline editorial.

## Runtime de app

1. La webapp lee `NN.json` directo desde disco.
2. No se usa SQLite para navegación ni lectura.
3. Modo lectura por defecto: `/story/<path>?p=N`.
4. Modo editorial: `/story/<path>?p=N&editor=1`.

## CLI vigente

1. `python manage.py runserver`
2. No existen comandos CLI de ingesta/adaptación en `app/`.

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

