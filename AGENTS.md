# AGENTS

## Propósito

Este repositorio es personal, pero se gestiona con criterios
profesionales. Cada cambio debe priorizar claridad, trazabilidad,
seguridad y repetibilidad.

## Reglas operativas

1. No ejecutar comandos persistentes sin petición explícita del usuario.
2. `runserver` y bucles interactivos están prohibidos por defecto.
3. Preferir validaciones finitas (`--help`, scripts acotados y límites).
4. Evitar acciones destructivas fuera del alcance de la tarea en curso.
5. Mantener una sola tarea planificada activa a la vez.
6. Tras cada plan aprobado, registrar la tarea y cerrar con commit.

## Reglas de contenido y paginación

1. La paginación de textos es adaptativa al archivo importado.
2. No existe un objetivo fijo obligatorio de 16 o 32 páginas.
3. El archivo `origen_md.md` define la cantidad real de páginas.
4. En `biblioteca/**/origen_md.md` no se fuerzan cortes de línea.

## Reglas de validación

1. Ejecutar comprobaciones finitas y reproducibles.
2. Registrar la validación en el archivo de tarea correspondiente.
3. Documentar límites o comprobaciones no ejecutadas, con su motivo.

## Sistema documental

1. Este archivo es la fuente operativa única del repositorio.
2. El detalle de ejecución vive en `docs/tasks/TAREA-*.md`.
3. El índice de tareas vive en `docs/tasks/INDICE.md`.
4. Las decisiones arquitectónicas viven en `docs/adr/`.
5. El contexto operativo mínimo vive en `docs/context/`.
6. `CHANGELOG.md` se mantiene breve y enlaza cada tarea cerrada.

## Convención de tareas

1. ID y nombre estándar: `TAREA-001-<slug>`.
2. La numeración es global y continua en todo el repositorio.
3. Fechas en tareas e índice: `dd/mm/aa HH:MM`.
4. Formato de commit: `Tarea 001: <resumen>`.

## Política ADR

Crear ADR solo para decisiones arquitectónicas, por ejemplo:

- gobernanza y contratos de proceso
- políticas de persistencia y datos
- contratos de importación y respaldo
- cambios estructurales de largo plazo

Estados permitidos:

- propuesto
- aceptado
- reemplazado
- obsoleto

## Flujo Git

1. Rama única: `main`.
2. Un commit por tarea planificada.
3. No usar ramas de funcionalidad salvo necesidad excepcional.

## Criterio de cierre de tarea

Una tarea se considera cerrada cuando:

1. El alcance acordado está implementado.
2. Se ejecutó validación finita y reproducible.
3. Se actualizó archivo de tarea e índice.
4. Se añadió entrada breve en `CHANGELOG.md`.
5. Se creó el commit final de la tarea.

## Política de datos

1. SQLite se mantiene en `db/`.
2. Los archivos de base de datos no se versionan.
3. Los flujos de importación y respaldo deben ser repetibles.

## Higiene de contexto

1. Mantener en `docs/context/` solo material operativo vigente.
2. Eliminar exportaciones redundantes con `.md` canónico.
3. Guardar referencias visuales en `docs/assets/style_refs/`.
