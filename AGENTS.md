# AGENTS

## Proposito

Este repositorio aplica un flujo profesional para el **Generador de cuentos ilustrados**.

## Reglas operativas

1. No ejecutar comandos persistentes sin peticion explicita del usuario.
2. `runserver` esta prohibido por defecto en tareas de validacion.
3. Preferir comandos finitos (`--help`, validaciones acotadas, timeouts).
4. Evitar acciones destructivas fuera del alcance de la tarea activa.
5. Tras cada plan aprobado: registrar tarea, actualizar indice/changelog, cerrar con un commit unico y hacer push a GitHub.

## Contrato de datos vigente

1. Fuente de verdad: `library/`.
2. Un libro se detecta por presencia de uno o mas archivos `NN.json` en su carpeta.
3. Cada cuento se guarda en un unico archivo `NN.json` (2 digitos).
4. Estructura canonica de `NN.json`:
   - top-level base: `schema_version`, `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `pages`.
   - top-level extension inicial de ingesta: `story_title`, `cover`, `source_refs`, `ingest_meta`.
   - por pagina: `page_number`, `status`, `text.original`, `text.current`, `images`.
   - `images.main` obligatorio, `images.secondary` opcional.
5. Cada slot de imagen define `status`, `prompt.original`, `prompt.current`, `active_id` y `alternatives[]`.
6. Cada alternativa define `id`, `slug`, `asset_rel_path`, `mime_type`, `status`, `created_at`, `notes`.
7. Los assets de imagen se nombran con formato opaco `img_<uuid>_<slug>.<ext>` y la relacion pagina/slot vive en JSON.
8. `library/_inbox/` se usa como bandeja de propuestas editoriales `.md` y referencias `.pdf`.
   - Para la skill `adaptacion-ingesta-inicial`, el contraste con `NN.pdf` es obligatorio por lote: si un cuento no tiene cobertura PDF util, la ejecucion falla.
   - La skill `adaptacion-ingesta-inicial` es 100% conversacional: no usa scripts ni CLI, y utiliza la skill `pdf` para contraste canonico.
9. `library/_backups/` es opcional para respaldos manuales.
10. Sidecars de revision vigentes en `library/<book>/_reviews/`:
    - `adaptation_context.json` (contexto y glosario por libro)
    - `NN.issues.json` (incoherencias/errores por cuento)
    - `NN.review.json` (maestro por cuento)
    - `NN.decisions.log.jsonl` (log final por hallazgo resuelto)
11. Sidecars legacy (`context_chain`, `glossary_merged`, `pipeline_state`, `NN.findings`, etc.) quedan fuera de contrato.

## Pipeline editorial

1. Las skills de adaptacion versionadas en este repositorio viven en `.codex/skills/`.
2. `app/` no ejecuta pipeline editorial.
3. `adaptacion-ingesta-inicial` se ejecuta en chat con preguntas una a una y opciones; la escritura es incremental sobre archivos finales.
4. Cualquier flujo editorial externo debe respetar este contrato de datos.

## Runtime de app

1. La webapp lee `NN.json` directo desde disco.
2. No se usa SQLite para navegacion ni lectura.
3. Home de biblioteca: `/`.
4. Navegacion de nodos: `/browse/<path>`.
5. Lectura por pagina: `/story/<path>/page/<int:page_number>`.
6. Modo editorial por pagina: `/editor/story/<path>/page/<int:page_number>`.
7. Fragmentos HTMX de lectura: `/fragments/story/<path>/page/<int:page_number>/*`.
8. Rutas legacy (`/n/<path>` y `/story/<path>?p=N[&editor=1]`) quedan como compatibilidad temporal con redirect.

## CLI vigente

1. `python manage.py runserver`
2. No existen comandos CLI de ingesta/adaptacion en `app/`.

## Sistema documental

1. Operacion principal en este archivo (`AGENTS.md`).
2. ADR en `docs/adr/` para decisiones arquitectonicas.
3. Tareas en `docs/tasks/` con indice en `docs/tasks/INDICE.md`.
4. `CHANGELOG.md` breve, siempre enlazando a la tarea correspondiente.

## Convencion de tareas

1. Formato: `TAREA-001-<slug>`.
2. Numeracion global continua del repositorio.
3. Fecha documental: `dd/mm/aa HH:MM`.
4. Mensaje de commit: `Tarea 001: <resumen>`.

## Flujo Git

1. Rama unica: `main`.
2. Un commit por tarea planificada.
3. No usar ramas funcionales salvo necesidad explicita.

## Cierre de tarea

Una tarea queda cerrada cuando:

1. El alcance pactado esta implementado.
2. Se ejecutaron validaciones finitas reproducibles.
3. Se actualizaron archivo de tarea, indice y changelog breve.
4. Se creo el commit final de la tarea.
