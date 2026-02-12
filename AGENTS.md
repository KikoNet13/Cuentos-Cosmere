# AGENTS

## Propósito

Este repositorio es personal, pero se gestiona con criterios profesionales.
Cada cambio debe priorizar:

- contexto claro
- decisiones trazables
- operación segura
- validaciones repetibles

## Reglas operativas

1. No ejecutar comandos de larga duración sin petición explícita.
2. `runserver`, observadores y bucles interactivos están prohibidos por defecto.
3. Priorizar validaciones finitas (`--help`, scripts cortos y l?mites`).
4. Evitar acciones destructivas fuera del alcance de la tarea en curso.
5. Mantener una sola tarea planificada activa a la vez.

## Reglas de validación

1. Ejecutar comprobaciones finitas y reproducibles.
2. Registrar la validación en el archivo de tarea correspondiente.
3. Documentar límites o comprobaciones no ejecutadas, con motivo.

## Sistema de documentación

1. El detalle operativo vive en `docs/tasks/TAREA-*.md`.
2. El índice de tareas vive en `docs/tasks/INDICE.md`.
3. Las decisiones arquitectónicas viven en `docs/adr/`.
4. `CHANGELOG.md` se mantiene breve y enlaza a cada tarea cerrada.

## Política ADR

Crear ADR solo para decisiones arquitectónicas, por ejemplo:

- contratos de proceso del repositorio
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
3. Formato vigente de commit: `tarea(TAREA-YYYYMMDD-HHMM): <resumen>`.
4. No usar ramas de funcionalidad salvo necesidad excepcional.

## Política de datos

1. SQLite se mantiene en `db/`.
2. Los archivos de base de datos no se versionan.
3. Los flujos de importación y respaldo deben ser repetibles.

## Higiene de contexto

1. El contexto activo vive en `docs/context/`.
2. Eliminar exportaciones redundantes cuando exista un `.md` canónico.
3. Referencias visuales en `docs/assets/style_refs/`.
