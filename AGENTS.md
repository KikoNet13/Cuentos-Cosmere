# AGENTS

## Propósito

Este repositorio es personal, pero se mantiene con estándares profesionales:
claridad, trazabilidad, seguridad y repetibilidad.

## Reglas operativas

1. No ejecutar comandos persistentes sin petición explícita del usuario.
2. `runserver` y bucles interactivos están prohibidos por defecto.
3. Preferir validaciones finitas (`--help`, scripts acotados y timeouts).
4. Evitar acciones destructivas fuera del alcance de la tarea activa.
5. Tras cada plan aprobado, registrar tarea y cerrar con commit único.

## Contrato de datos vigente

1. Fuente de verdad: `biblioteca/`.
2. Cuento canónico: carpeta con `meta.md` y páginas `NNN.md`.
3. Prompt y narrativa se editan solo en `.md`.
4. La UI no edita texto ni prompt; solo lee/copia y guarda imágenes.
5. La paginación depende del archivo importado, sin objetivo fijo 16/32.

## Caché y sincronización

1. SQLite se usa como caché temporal de lectura rápida.
2. La caché se marca stale por fingerprint global de `biblioteca/`.
3. Si está stale, se bloquean escrituras de imagen en UI.
4. El refresco de caché se hace con `python manage.py rebuild-cache`.

## Sistema documental

1. Este archivo es la guía operativa principal.
2. Tareas: `docs/tasks/TAREA-*.md`.
3. Índice de tareas: `docs/tasks/INDICE.md`.
4. Decisiones arquitectónicas: `docs/adr/`.
5. `CHANGELOG.md` se mantiene breve con referencia a tarea.

## Convención de tareas

1. Formato: `TAREA-001-<slug>`.
2. Numeración global continua del repositorio.
3. Fecha en documentos: `dd/mm/aa HH:MM`.
4. Mensaje de commit: `Tarea 001: <resumen>`.

## Flujo Git

1. Rama única: `main`.
2. Un commit por tarea planificada.
3. No usar ramas funcionales salvo necesidad excepcional.

## Cierre de tarea

Una tarea se cierra cuando:

1. El alcance pactado está implementado.
2. Se ejecutó validación finita reproducible.
3. Se actualizaron archivo de tarea, índice y changelog breve.
4. Se creó el commit final de la tarea.
