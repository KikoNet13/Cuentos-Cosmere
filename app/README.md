# Cuentos Cosmere (App)

## Tecnologias

- Flask
- Peewee
- SQLite

## Flujo local con Pipenv

1. `pipenv install`
2. `pipenv run python manage.py init-db`
3. `pipenv run python manage.py migrate-models-v3`
4. `pipenv run python manage.py import`
5. `pipenv run python manage.py runserver --help`

## Modelo v3

- `Pagina`: texto por numero dentro de un cuento.
- `Ancla` y `AnclaVersion`: referencias versionables por saga.
- `Imagen`: pertenece a `Pagina` o `AnclaVersion`.
- `ImagenRequisito`: requisitos mixtos (`ancla_version` o `imagen`).

## Contrato de importacion

- El importador toma paginas desde `biblioteca/**/origen_md.md`.
- Actualiza paginas por `(cuento, numero)`.
- Elimina paginas no presentes en el archivo importado.
- No importa prompts legacy.

## Respaldos

- `pipenv run python manage.py export-imagenes`
- `pipenv run python manage.py import-imagenes`

Alias deprecados (compatibilidad):

- `pipenv run python manage.py export-prompts`
- `pipenv run python manage.py import-prompts`