# AGENTS

## Propósito

Este repositorio aplica un flujo profesional para el
**Generador de cuentos ilustrados**.

## Reglas operativas

1. No ejecutar comandos persistentes sin petición explícita del usuario.
2. `runserver` está prohibido por defecto en tareas de validación.
3. Preferir comandos finitos (`--help`, validaciones acotadas, timeouts).
4. Evitar acciones destructivas fuera del alcance de la tarea activa.
5. Tras cada plan aprobado: registrar tarea, actualizar índice/changelog, cerrar con un commit único y hacer push a GitHub.

## Contrato de datos vigente

1. Fuente de verdad: `library/`.
2. Un libro se detecta por presencia de uno o más archivos `NN.md` en su carpeta.
3. Cada cuento es un único archivo `NN.md` (2 dígitos) dentro del libro.
4. Estructura canónica de `NN.md`: `## Meta`, `## Página NN`, `### Texto`, `### Prompts`, `#### <slot>`, `##### Requisitos`.
5. Los requisitos se expresan con lista tipada `tipo/ref` en bloque YAML.
6. Los PDFs de referencia viven junto al cuento con nombre `NN.pdf`.
7. `anclas.md` por libro es opcional pero recomendado.

## Flujo de ingestión

1. Entrada genérica en `library/_inbox/<batch_id>/input.md`.
2. Normalización/propuesta con `python manage.py inbox-parse --input <ruta> --book <book_rel_path> --story-id <NN>`.
3. Revisión de `review.md` y `manifest.json` antes de aplicar.
4. Aplicación explícita con `python manage.py inbox-apply --batch-id <id> --approve`.
5. Toda aplicación reconstruye caché automáticamente.

## Caché y sincronización

1. SQLite se usa solo como caché temporal (`db/library_cache.sqlite`).
2. La desactualización se detecta por fingerprint global de `library/`.
3. Si la caché está stale, se bloquean escrituras de imágenes en UI.
4. El refresco manual se ejecuta con `python manage.py rebuild-cache`.

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
