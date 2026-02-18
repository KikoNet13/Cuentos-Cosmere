# AGENTS

## Proposito

Este repositorio opera como plataforma orquestadora del flujo 3 IAs para cuentos ilustrados.

## Reglas operativas

1. No ejecutar comandos persistentes sin peticion explicita del usuario.
2. `runserver` esta prohibido por defecto en tareas de validacion.
3. Preferir comandos finitos (`--help`, validaciones acotadas, timeouts).
4. Evitar acciones destructivas fuera del alcance de la tarea activa.
5. Tras cada plan aprobado: registrar tarea, actualizar indice/changelog, cerrar con un commit único y hacer push a GitHub.

## Flujo 3 IAs (oficial)

1. NotebookLM:
   - fuente de generación editorial;
   - trabaja por prompts preparados por Codex;
   - flujo esperado:
     - plan de colección,
     - meta/anclas (`meta.json`),
     - cuentos (`NN.json` o partes `NN_a/_b` + fallback `a1/a2/b1/b2`);
   - entrega en `library/_inbox/<book_title>/`.
2. Codex (este repo):
   - prepara comunicacion con NotebookLM via skill dedicada;
   - válida contrato, fusiona partes en memoria, enriquece `reference_ids` y importa lotes;
   - genera/regenera `library/<book_rel_path>/chatgpt_project_setup.md` para operar ChatGPT Project por saga;
   - permite refresh manual del dossier sin reimportar cuentos;
   - emite mensajes accionables para NotebookLM;
   - facilita prompts y gestion de assets para ChatGPT Project.
3. ChatGPT Project:
   - genera imágenes a partir de prompts/anchors;
   - devuelve archivos para importarlos en su slot/ancla correcto.

Notas:

- El orquestador documental vive en este archivo (`AGENTS.md`), sin playbooks paralelos.
- Skills activas del flujo: `notebooklm-comunicacion` + `ingesta-cuentos`.
- La webapp incluye flujo guiado de relleno: `/_flow/image` (anclas primero).

## Contrato de datos vigente

1. Fuente de verdad: `library/`.
2. Un libro se detecta por presencia de uno o más archivos `NN.json` en su carpeta.
3. Cada cuento se guarda en un único archivo `NN.json` (2 digitos).
4. Estructura canónica de `NN.json`:
   - top-level obligatorio: `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
   - por página: `page_number`, `text`, `images`.
   - `images.main` obligatorio, `images.secondary` opcional.
5. Contrato de slot de imagen (`cover` y `images.*`):
   - `status`, `prompt`, `active_id`, `alternatives[]`, `reference_ids[]` (opcional).
6. Convencion operativa de `reference_ids`:
   - deben referenciar filenames de `meta.anchors[].image_filenames[]`.
   - no usar IDs opacos de assets finales como convencion principal.
7. Contrato de alternativa:
   - `id` (filename con extension),
   - `slug`,
   - `asset_rel_path`,
   - `mime_type`,
   - `status`,
   - `created_at`,
   - `notes`.
8. Los assets de imagen se nombran con formato opaco `<uuid>_<slug>.<ext>`.
9. Todos los assets de nodo viven en `library/<node>/images/`.
10. Cada nodo mantiene `library/<node>/images/index.json` con:
   - `filename`, `asset_rel_path`, `description`, `node_rel_path`, `created_at`.
11. `library/_inbox/` es la bandeja de entrada oficial:
    - `NN.json` por cuento, o partes `NN_a.json` + `NN_b.json`;
    - fallback permitido: `NN_a1.json`, `NN_a2.json`, `NN_b1.json`, `NN_b2.json`;
    - `meta.json` opcional por lote (recomendado para flujo listo de imagen);
    - `.md/.pdf` se ignoran en la ingesta nueva.
12. Compatibilidad de codificacion de entrada:
    - JSON UTF-8 y UTF-8 BOM aceptados.
13. `meta.json` por jerarquia:
    - `library/meta.json` (global),
    - `library/<node>/meta.json` (ancestros + libro),
    - minimos: `collection.title`, `anchors[]`, `updated_at`.
14. Sidecars legacy de adaptación (`adaptation_context.json`, `NN.issues.json`, etc.) quedan fuera de contrato.
15. Archivado post-import:
    - al completar un lote sin pendientes, mover `library/_inbox/<book_title>/` a `library/_processed/<book_title>/<timestamp>/`.
16. Artefacto operativo por saga:
    - `library/<book_rel_path>/chatgpt_project_setup.md`.
    - se regenera en cada ingesta válida y admite refresh manual.

## Pipeline editorial

1. Las skills versionadas en este repositorio viven en `.codex/skills/`.
2. Skills activas:
   - `.codex/skills/notebooklm-comunicacion/` para plan de colección, meta/anclas, prompting por partes y fallback.
   - `.codex/skills/ingesta-cuentos/` para fusion en memoria, validacion, enriquecimiento de refs, importacion y dossier de ChatGPT Project.
3. `app/` no ejecuta pipeline editorial autonomo; solo consume y edita contrato final.
4. Cualquier flujo externo debe respetar este contrato.

## Runtime de app

1. La webapp lee `NN.json` directo desde disco.
2. No se usa SQLite para navegación ni lectura.
3. Home de biblioteca: `/`.
4. Ruta canónica única para nodo/cuento: `/<path_rel>`.
5. Lectura de cuento:
   - `/<book>/<NN>` (página 1 por defecto).
   - `/<book>/<NN>?p=N`.
6. Edición de cuento:
   - `/<book>/<NN>?p=N&editor=1` (editor de página).
   - `/<book>/<NN>?editor=1` (editor de portada a nivel cuento).
7. Fragmentos HTMX de lectura:
   - `GET /<story_path>/_fr/shell?p=N`
   - `GET /<story_path>/_fr/advanced?p=N`
   - `POST /<story_path>/_fr/slot/<slot_name>/activate?p=N`
8. Acciones editoriales:
   - `POST /<story_path>/_act/page/save?p=N`
   - `POST /<story_path>/_act/page/slot/<slot_name>/upload?p=N`
   - `POST /<story_path>/_act/page/slot/<slot_name>/activate?p=N`
   - `POST /<story_path>/_act/cover/save`
   - `POST /<story_path>/_act/cover/upload`
   - `POST /<story_path>/_act/cover/activate`
   - `POST /<story_path>/_act/anchors/*`
9. Rutas legacy removidas (sin redirects): `/browse/*`, `/story/*`, `/editor/story/*`, `/n/*`.
10. Flujo guiado de imagen:
   - `GET /_flow/image` (muestra solo el primer pendiente global).
   - `POST /_flow/image/submit` (pegar y guardar, avanza al siguiente pendiente).

## CLI vigente

1. `python manage.py runserver`
2. No existen comandos CLI de ingesta/adaptacion en `app/`.

## Mensajeria orquestadora (Codex)

Codex debe poder producir estos bloques para el usuario:

1. Setup NotebookLM (checklist + prompt base de plan de colección).
2. Prompt de `meta.json` (anclas + `style_rules` + `continuity_rules`).
3. Prompts de cuentos por partes con fallback (`8+8` -> `4+4`).
4. Delta update estructurado para reentregas parciales de NotebookLM.
5. Setup ChatGPT Project (checklist + prompt base de continuidad visual).

## Sistema documental

1. Operación principal en este archivo (`AGENTS.md`).
2. ADR en `docs/adr/` para decisiones arquitectonicas.
3. Tareas en `docs/tasks/` con índice en `docs/tasks/INDICE.md`.
4. `CHANGELOG.md` breve, siempre enlazando a la tarea correspondiente.

## Convencion de tareas

1. Formato: `TAREA-001-<slug>`.
2. Numeracion global continua del repositorio.
3. Fecha documental: `dd/mm/aa HH:MM`.
4. Mensaje de commit: `Tarea 001: <resumen>`.

## Flujo Git

1. Rama única: `main`.
2. Un commit por tarea planificada.
3. No usar ramas funcionales salvo necesidad explicita.

## Cierre de tarea

Una tarea queda cerrada cuando:

1. El alcance pactado esta implementado.
2. Se ejecutaron validaciones finitas reproducibles.
3. Se actualizaron archivo de tarea, índice y changelog breve.
4. Se creo el commit final de la tarea.
