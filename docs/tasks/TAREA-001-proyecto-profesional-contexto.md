# TAREA-001-proyecto-profesional-contexto

## Metadatos

- ID de tarea: TAREA-001-proyecto-profesional-contexto
- Fecha: 12/02/26 11:05
- Estado: cerrada
- Responsable: local
- ADR relacionadas: 0001, 0002, 0003

## Objetivo

Formalizar gobernanza del repositorio y trazabilidad escalable con
`AGENTS.md`, ADR, tareas por archivo, registro breve de cambios y
curación de contexto.

## Contexto

El repositorio tenía código y datos de ejecución, pero faltaban:

- contrato operativo en raíz
- decisiones arquitectónicas registradas
- estructura escalable de tareas
- base Git y política de ignore
- ubicación canónica para contexto y referencias visuales

## Plan

1. Crear documentos y plantillas de gobernanza.
2. Crear ADR base para proceso, datos e importación y respaldo.
3. Introducir sistema de tareas con índice y una tarea inicial.
4. Curar `contexto/` y `ejemplos/` hacia estructura `docs/`.
5. Inicializar Git en `main` y ajustar ignore.

## Decisiones

- Usar tareas detalladas y registro breve de cambios por cierre.
- Mantener SQLite en `db/` y excluir archivos de estado local.
- Limitar ADR a decisiones arquitectónicas.
- Prohibir comandos persistentes por defecto.

## Cambios aplicados

- Archivos raíz: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `.gitignore`.
- Contrato operativo consolidado en `AGENTS.md`.
- Sistema ADR inicial en `docs/adr/`.
- Sistema de tareas en `docs/tasks/`.
- Curación de activos heredados hacia `docs/context/`.
- Curación de activos heredados hacia `docs/assets/style_refs/`.

## Validación ejecutada

- Verificación de estructura y presencia de archivos obligatorios.
- Búsqueda de referencias obsoletas a exportaciones HTML eliminadas.
- Respeto de política de comandos finitos.

## Riesgos

- Parte del contexto histórico puede requerir limpieza editorial adicional.

## Seguimiento

- Configurar remoto GitHub y publicar `main`.
- Continuar con normalización de documentación en castellano.

## Commit asociado

- Mensaje de commit: `Tarea 001: profesionalizar gobernanza y trazabilidad`
- Hash de commit: `52243f6`
