# TAREA-006-library-inbox-nnmd-skill-ingesta

## Metadatos

- ID de tarea: `TAREA-006-library-inbox-nnmd-skill-ingesta`
- Fecha: 12/02/26 20:30
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0004`, `0005`

## Objetivo

Aplicar el contrato actualizado de datos con `library/` como raíz, flujo de ingestión en `library/_inbox`, cuento por archivo `NN.md` con secciones de texto/prompts, y skill operativa para parsear/revisar/aplicar.

## Contexto

La base de código y la documentación aún estaban en transición entre `biblioteca` y `library`, y faltaba cerrar el flujo completo de ingestión con validaciones reproducibles.

## Plan

1. Cerrar backend y CLI para el contrato `NN.md` + `_inbox`.
2. Renombrar físicamente la raíz de datos a `library`.
3. Validar migración de layout legacy a libro plano y caché.
4. Documentar el contrato vigente y registrar trazabilidad.
5. Crear skill global de ingestión para uso repetible.

## Decisiones

- `library/` queda como único nombre canónico de raíz de datos.
- El formato de cuento vigente es archivo único `NN.md` por libro.
- Se mantiene parseo tolerante de página (`Página 1`), con salida normalizada (`Página 01`) al aplicar.
- El archivado de carpetas legacy no bloquea la migración si hay restricciones de permisos.
- Se ignoran artefactos locales de flujo (`_inbox`, `_backups`, `_legacy_story_dirs`) en Git.

## Cambios aplicados

- Código:
  - `app/config.py`
  - `app/library_fs.py`
  - `app/library_cache.py`
  - `app/library_migration.py`
  - `app/notebooklm_ingest.py`
  - `app/routes_v3.py`
  - `manage.py`
- UI:
  - `app/templates/base.html`
  - `app/templates/dashboard.html`
  - `app/templates/node.html`
  - `app/templates/cuento.html`
- Datos:
  - renombre de raíz `biblioteca/` -> `library/`
  - consolidación canónica en `library/.../01.md` a `06.md`
  - creación de PDFs planos `library/.../01.pdf` a `05.pdf`
  - eliminación de carpetas legacy versionadas (`01/..05/` y `prompts/`)
  - prueba de ingestión aplicada: `library/.../06.md`
- Documentación:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/context/INDICE.md`
  - `docs/adr/0003-contrato-importacion-respaldo.md`
  - `docs/adr/0004-biblioteca-fuente-verdad-cache-temporal.md`
  - `docs/adr/0005-contrato-library-inbox-nnmd.md`
  - `docs/adr/INDICE.md`
- Skill global:
  - `C:/Users/Kiko/.codex/skills/notebooklm-ingest/SKILL.md`
  - `C:/Users/Kiko/.codex/skills/notebooklm-ingest/references/checklist.md`

## Validación ejecutada

- `python manage.py --help`
- `python manage.py migrate-library-layout --help`
- `python manage.py inbox-parse --help`
- `python manage.py inbox-apply --help`
- `python manage.py rebuild-cache --help`
- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py inbox-parse --input tmp/01.md --book nacidos-de-la-bruma-era-1/el-imperio-final --story-id 06`
- `python manage.py inbox-apply --batch-id 20260212-192558-06 --approve`
- `python manage.py rebuild-cache`
- validación de sintaxis AST local de `manage.py` y `app/*.py`

## Riesgos

- En este entorno, SQLite de caché opera en backend `:memory:` por restricciones de escritura en archivos temporales.
- El archivado de carpetas legacy puede dar warnings de permisos; no bloquea la creación de `NN.md`.

## Seguimiento

1. Revisar si quieres eliminar físicamente carpetas legacy (`01/..05/`) cuando no sean necesarias.
2. Añadir reglas de parseo específicas para tu formato final de entrada si NotebookLM cambia el layout.
3. Si quieres automatizar más, añadir `agents/openai.yaml` a la skill global cuando esté disponible `PyYAML`.

## Commit asociado

- Mensaje de commit:
  `Tarea 006: library inbox, contrato NN.md y skill de ingestión`
- Hash de commit: `pendiente`
