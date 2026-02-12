# Cuentos Cosmere

## Tecnolog?as

- Flask
- Peewee
- SQLite
- HTMX

## Inicio r?pido con Pipenv

1. Instalar dependencias.

```powershell
pipenv install
```

1. Crear el esquema de base de datos.

```powershell
pipenv run python manage.py init-db
```

1. Migrar textos heredados a p?ginas, si aplica.

```powershell
pipenv run python manage.py migrate-texto-pages
```

1. Importar el dataset can?nico desde `biblioteca/`.

```powershell
pipenv run python manage.py import
```

1. Validar el comando del servidor sin dejar procesos abiertos.

```powershell
pipenv run python manage.py runserver --help
```

1. Iniciar servidor solo cuando se necesite trabajar interfaz.

```powershell
pipenv run python manage.py runserver --debug
```

1. Abrir en navegador.

`http://127.0.0.1:5000`

## Respaldo de prompts

- Exportar prompts desde SQLite a JSON.

```powershell
pipenv run python manage.py export-prompts
```

- Importar prompts desde JSON a SQLite.

```powershell
pipenv run python manage.py import-prompts
```

## Convenci?n de c?digos de cuento

- C?digo por libro: `2` d?gitos num?ricos (`01`, `02`, `03`, ...).
- El c?digo no incluye el n?mero del libro.
