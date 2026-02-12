# TAREA-20260212-1105-proyecto-profesional-contexto

## Metadatos

- ID de tarea: TAREA-20260212-1105-proyecto-profesional-contexto
- Fecha: 2026-02-12 11:05
- Estado: cerrada
- Responsable: local
- ADR relacionadas: 0001, 0002, 0003

## Objetivo

Formalizar gobernanza del repositorio y trazabilidad escalable con
`AGENTS.md`, ADR, tareas por archivo, registro breve de cambios y
curaci?n de contexto.

## Contexto

El repositorio ten?a c?digo y datos de ejecuci?n, pero faltaban:

- contrato operativo en ra?z
- decisiones arquitect?nicas registradas
- estructura escalable de tareas
- base Git y pol?tica de ignore
- ubicaci?n can?nica para contexto y referencias visuales

## Plan

1. Crear documentos y plantillas de gobernanza.
1. Crear ADR base para proceso, datos e importaci?n y respaldo.
1. Introducir sistema de tareas con ?ndice y una tarea inicial.
1. Curar `contexto/` y `ejemplos/` hacia estructura `docs/`.
1. Inicializar Git en `main` y ajustar ignore.

## Decisiones

- Usar tareas detalladas y registro breve de cambios por cierre.
- Mantener SQLite en `db/` y excluir archivos de estado local.
- Limitar ADR a decisiones arquitect?nicas.
- Prohibir comandos persistentes por defecto.

## Cambios aplicados

- Archivos ra?z: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `.gitignore`.
- Gu?as: `docs/estandares_proyecto.md`, `docs/operacion_segura.md`.
- Gu?as: `docs/flujo_git.md`.
- Sistema ADR inicial en `docs/adr/`.
- Sistema de tareas en `docs/tasks/`.
- Curaci?n de activos heredados hacia `docs/context/`.
- Curaci?n de activos heredados hacia `docs/assets/style_refs/`.

## Validaci?n ejecutada

- Verificaci?n de estructura y presencia de archivos obligatorios.
- B?squeda de referencias obsoletas a exportaciones HTML eliminadas.
- Respeto de pol?tica de comandos finitos.

## Riesgos

- Parte del contexto hist?rico puede requerir limpieza editorial adicional.

## Seguimiento

- Configurar remoto GitHub y publicar `main`.
- Ejecutar tarea de normalizaci?n integral de Markdown y castellano.

## Commit asociado

- Mensaje de commit: `tarea(TAREA-20260212-1105): gobernanza y trazabilidad`.
- Hash de commit: `52243f6`.
