# TAREA-009-limpieza-library-el-imperio-final

## Metadatos

- ID de tarea: `TAREA-009-limpieza-library-el-imperio-final`
- Fecha: 13/02/26 13:44
- Estado: cerrada
- Responsable: local
- ADR relacionadas: (ninguna)

## Objetivo

Reflejar en GitHub la limpieza local de `library/nacidos-de-la-bruma-era-1/el-imperio-final` para reiniciar el flujo editorial desde cero con la skill oficial.

## Contexto

El usuario elimino localmente archivos `NN.md` y `NN.pdf` legacy de `library/.../el-imperio-final` y solicito sincronizar esa eliminacion en el remoto.

## Plan

1. Confirmar estado git con eliminaciones pendientes en `library/...`.
2. Actualizar trazabilidad documental (`TAREA-009`, `INDICE`, `CHANGELOG`).
3. Crear un unico commit y hacer push a `main`.

## Decisiones

- Se elimina solo contenido legacy del libro en `library/...`, sin tocar `library/_inbox`.
- La configuracion local `.codex/config.toml` no se versiona en este commit.

## Cambios aplicados

- Eliminados:
  - `library/nacidos-de-la-bruma-era-1/anclas.md`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/01.md`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/01.pdf`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/02.md`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/02.pdf`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/03.md`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/03.pdf`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/04.md`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/04.pdf`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/05.md`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/05.pdf`
  - `library/nacidos-de-la-bruma-era-1/el-imperio-final/06.md`
- Documentacion:
  - `docs/tasks/TAREA-009-limpieza-library-el-imperio-final.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

- `git status --short`
- `git diff --name-status`

## Riesgos

- Si algun flujo aun depende de `NN.md`/`NN.pdf` legacy, quedara sin datos hasta completar adaptacion a `NN.json`.

## Seguimiento

1. Ejecutar la skill `revision-orquestador-editorial` sobre `library/_inbox/El imperio final` hacia `cosmere/nacidos-de-la-bruma-era-1/el-imperio-final`.

## Commit asociado

- Mensaje de commit: `Tarea 009: limpieza library de El imperio final`
- Hash de commit: pendiente

