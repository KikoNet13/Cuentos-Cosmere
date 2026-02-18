# AGENTS

## Proposito

Este repositorio opera como plataforma orquestadora del flujo 3 IAs para cuentos ilustrados.

## Reglas operativas

1. No ejecutar comandos persistentes sin peticion explicita del usuario.
2. `runserver` esta prohibido por defecto en tareas de validacion.
3. Preferir comandos finitos (`--help`, validaciones acotadas, timeouts).
4. Evitar acciones destructivas fuera del alcance de la tarea activa.
5. Tras cada plan aprobado: registrar tarea, actualizar indice/changelog, cerrar con un commit unico y hacer push a GitHub.

## Flujo 3 IAs (oficial)

1. NotebookLM:
   - fuente de generacion editorial;
   - entrega `NN.json` y opcional `meta.json` en `library/_inbox/<book_title>/`.
2. Codex (este repo):
   - valida contrato, mueve/importa lotes y mantiene app;
   - emite mensajes accionables para NotebookLM;
   - facilita prompts y gestion de assets para ChatGPT Project.
3. ChatGPT Project:
   - genera imagenes a partir de prompts/anchors;
   - devuelve archivos para importarlos en su slot/ancla correcto.

Notas:

- El orquestador documental vive en este archivo (`AGENTS.md`), sin playbooks paralelos.
- La skill activa de ingesta es `ingesta-cuentos`.

## Contrato de datos vigente

1. Fuente de verdad: `library/`.
2. Un libro se detecta por presencia de uno o mas archivos `NN.json` en su carpeta.
3. Cada cuento se guarda en un unico archivo `NN.json` (2 digitos).
4. Estructura canonica de `NN.json`:
   - top-level obligatorio: `story_id`, `title`, `status`, `book_rel_path`, `created_at`, `updated_at`, `cover`, `pages`.
   - por pagina: `page_number`, `text`, `images`.
   - `images.main` obligatorio, `images.secondary` opcional.
5. Contrato de slot de imagen (`cover` y `images.*`):
   - `status`, `prompt`, `active_id`, `alternatives[]`, `reference_ids[]` (opcional).
6. Contrato de alternativa:
   - `id` (filename con extension),
   - `slug`,
   - `asset_rel_path`,
   - `mime_type`,
   - `status`,
   - `created_at`,
   - `notes`.
7. Los assets de imagen se nombran con formato opaco `<uuid>_<slug>.<ext>`.
8. Todos los assets de nodo viven en `library/<node>/images/`.
9. Cada nodo mantiene `library/<node>/images/index.json` con:
   - `filename`, `asset_rel_path`, `description`, `node_rel_path`, `created_at`.
10. `library/_inbox/` es la bandeja de entrada oficial:
    - `NN.json` por cuento;
    - `meta.json` opcional por lote;
    - `.md/.pdf` se ignoran en la ingesta nueva.
11. `meta.json` por jerarquia:
    - `library/meta.json` (global),
    - `library/<node>/meta.json` (ancestros + libro),
    - minimos: `collection.title`, `anchors[]`, `updated_at`.
12. Sidecars legacy de adaptacion (`adaptation_context.json`, `NN.issues.json`, etc.) quedan fuera de contrato.

## Pipeline editorial

1. Las skills versionadas en este repositorio viven en `.codex/skills/`.
2. Skill de ingesta activa: `.codex/skills/ingesta-cuentos/` (conversacional, sin scripts).
3. `app/` no ejecuta pipeline editorial autonomo; solo consume y edita contrato final.
4. Cualquier flujo externo debe respetar este contrato.

## Runtime de app

1. La webapp lee `NN.json` directo desde disco.
2. No se usa SQLite para navegacion ni lectura.
3. Home de biblioteca: `/`.
4. Ruta canonica unica para nodo/cuento: `/<path_rel>`.
5. Lectura de cuento:
   - `/<book>/<NN>` (pagina 1 por defecto).
   - `/<book>/<NN>?p=N`.
6. Edicion de cuento:
   - `/<book>/<NN>?p=N&editor=1` (editor de pagina).
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

## CLI vigente

1. `python manage.py runserver`
2. No existen comandos CLI de ingesta/adaptacion en `app/`.

## Mensajeria orquestadora (Codex)

Codex debe poder producir estos bloques para el usuario:

1. Setup NotebookLM (checklist + prompt base de salida JSON).
2. Setup ChatGPT Project (checklist + prompt base de continuidad visual).
3. Delta update estructurado para reentregas parciales de NotebookLM.

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
