# AGENTS

## Proposito

Este repositorio aplica un flujo profesional para el
**Generador de cuentos ilustrados**.

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
   - top-level: `schema_version`, `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `pages`.
   - por pagina: `page_number`, `status`, `text.original`, `text.current`, `images`.
   - `images.main` obligatorio, `images.secondary` opcional.
5. Cada slot de imagen define `status`, `prompt.original`, `prompt.current`, `active_id` y `alternatives[]`.
6. Cada alternativa define `id`, `slug`, `asset_rel_path`, `mime_type`, `status`, `created_at`, `notes`.
7. Los assets de imagen se nombran con formato opaco `img_<uuid>_<slug>.<ext>` y la relacion pagina/slot vive en JSON.
8. `library/_inbox/` se usa como bandeja de propuestas editoriales `.md` y referencias `.pdf`.
9. `library/_backups/` es opcional para respaldos manuales.

## Flujo editorial oficial

1. Flujo principal: skill `revision-adaptacion-editorial`.
2. La skill detecta libros en `library/_inbox/`.
3. La skill pide nodos destino una sola vez por libro.
4. La skill revisa/adapta cada cuento y escribe/actualiza `NN.json` en `library/...`.
5. Se conserva comparativa editorial en `text.original/current` y `prompt.original/current`.
6. La gestion de alternativas de imagen y activa se hace sobre el JSON del cuento.
7. En TAREA-008 no se ejecuta migracion real de `_inbox`; solo queda el procedimiento listo en skill y app.

## Runtime de app

1. La webapp lee `NN.json` directo desde disco.
2. No se usa SQLite para navegacion ni lectura.
3. No hay cache stale por fingerprint en este contrato.

## CLI vigente

1. `python manage.py runserver`
2. No existen comandos CLI de ingesta en el flujo oficial.

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
