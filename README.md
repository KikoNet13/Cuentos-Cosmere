# Cuentos Cosmere

Proyecto personal de cuentos ilustrados con flujo profesional.

## Tecnologias

- Flask
- Peewee
- SQLite
- HTMX (opcional)
- Pipenv

## Inicio rapido

1. `pipenv install`
2. `pipenv run python manage.py init-db`
3. `pipenv run python manage.py migrate-models-v3`
4. `pipenv run python manage.py import`
5. `pipenv run python manage.py runserver --help`

## Contrato funcional

- La pagina es la unidad narrativa editable del cuento.
- La imagen pertenece a una pagina o a una version de ancla.
- Las anclas se versionan por saga (`Ancla` + `AnclaVersion`).
- La paginacion depende del archivo `origen_md.md` importado.
- `import` sincroniza solo paginas y referencias PDF.

## Respaldo de imagenes

- Exportar: `pipenv run python manage.py export-imagenes`
- Importar: `pipenv run python manage.py import-imagenes`
- `export-prompts` e `import-prompts` quedan como alias deprecados.

## Convenciones del repositorio

- Operacion: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Contexto: `docs/context/`