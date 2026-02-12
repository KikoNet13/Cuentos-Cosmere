# Cuentos Cosmere

Proyecto personal con estándares de trabajo profesionales.

## Tecnologías

- Flask
- Peewee
- SQLite
- HTMX
- Pipenv

## Inicio rápido

1. `pipenv install`
2. `pipenv run python manage.py init-db`
3. `pipenv run python manage.py migrate-texto-pages`
4. `pipenv run python manage.py import`
5. `pipenv run python manage.py runserver --help`

## Convenciones del repositorio

- Contrato operativo y flujo de trabajo: `AGENTS.md`
- Trazabilidad de tareas: `docs/tasks/`
- Decisiones arquitectónicas: `docs/adr/`
- Contexto operativo: `docs/context/`

## Contrato de paginación

- La cantidad de páginas depende del archivo importado.
- Si quieres cuentos de 16 páginas, debes preparar el archivo con 16.
- El sistema mantiene compatibilidad con archivos legacy de más páginas.

## Datos y contenido

- Contenido canónico de cuentos: `biblioteca/`
- Estado local de base de datos: `db/` (no versionado)
- Referencia de prompts: `biblioteca/.../prompts/era1_prompts_data.json`

## Referencia de la app

La guía específica de la aplicación está en `app/README.md`.
