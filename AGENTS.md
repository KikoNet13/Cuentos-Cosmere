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
2. Un libro se detecta por presencia de uno o mas archivos `NN.md` en su carpeta.
3. Cada cuento es un unico archivo `NN.md` (2 digitos) dentro del libro.
4. Estructura canonica de `NN.md`: `## Meta`, `## Pagina NN`, `### Texto`, `### Prompts`, `#### <slot>`, `##### Requisitos`.
5. Los requisitos se expresan con lista tipada `tipo/ref` en bloque YAML.
6. Los PDFs de referencia viven junto al cuento con nombre `NN.pdf`.
7. `anclas.md` por libro es opcional pero recomendado.
8. `meta.md` es opcional por nodo; cuando existe, puede incluir `## Glosario` en tabla Markdown con columnas `termino|canonico|permitidas|prohibidas|notas`.
9. El glosario se resuelve de forma jerarquica (raiz -> nodo libro), y el nodo mas especifico sobrescribe terminos repetidos.

## Flujo de ingestion

1. Entrada manual pendiente en `library/_pending/` (archivos fuente `.md`).
2. Normalizacion/propuesta con `python manage.py inbox-parse --input <ruta> --book <book_rel_path> --story-id <NN>`.
3. Artefactos de trabajo generados en `library/_inbox/<batch_id>/`.
4. Revisar `review.md`, `ai_context.json`, `review_ai.md`, `review_ai.json` y `manifest.json`.
5. Validar `review_ai.json` con `python manage.py inbox-review-validate --batch-id <id>`.
6. Aplicar con `python manage.py inbox-apply --batch-id <id> --approve`.
7. Si se fuerza la aplicacion, exigir `--force --force-reason "..."`; el override queda trazado en `manifest.json`.
8. Toda aplicacion reconstruye cache automaticamente.

## Cache y sincronizacion

1. SQLite se usa solo como cache temporal (`db/library_cache.sqlite`).
2. La desactualizacion se detecta por fingerprint global de `library/`.
3. Si la cache esta stale, se bloquean escrituras de imagenes en UI.
4. El refresco manual se ejecuta con `python manage.py rebuild-cache`.

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
