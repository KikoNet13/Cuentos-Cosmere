# AGENTS

## Propósito

Este repositorio aplica un flujo profesional para desarrollar el
**Generador de cuentos ilustrados**.

## Reglas operativas

1. No ejecutar comandos persistentes sin petición explícita del usuario.
2. `runserver` está prohibido por defecto en tareas de validación.
3. Preferir comandos finitos (`--help`, validaciones acotadas, timeouts).
4. Evitar acciones destructivas fuera del alcance de la tarea activa.
5. Tras cada plan aprobado: registrar tarea, actualizar índice/changelog y cerrar
   con un commit único.

## Contrato de datos vigente

1. Fuente de verdad: `biblioteca/`.
2. Un cuento canónico es una carpeta con `meta.md` y páginas `NNN.md`.
3. El frontmatter se mantiene en castellano (`pagina`, `imagenes`, `requisitos`).
4. La UI no edita narrativa ni prompts: solo lectura/copia y guardado de imágenes.
5. La paginación depende del archivo importado, sin objetivo fijo de páginas.

## Caché y sincronización

1. SQLite se usa solo como caché temporal (`db/library_cache.sqlite`).
2. La desactualización se detecta por fingerprint global de `biblioteca/`.
3. Si la caché está stale, se bloquean escrituras de imágenes en UI.
4. El refresco se ejecuta con `python manage.py rebuild-cache`.

## Sistema documental

1. Operación principal en este archivo (`AGENTS`).
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
