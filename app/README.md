# Cuentos Cosmere

## Tecnologías

- Flask
- Peewee
- SQLite
- HTMX

## Inicio rápido con Pipenv

1. Instalar dependencias.

```powershell
pipenv install
```

1. Crear el esquema de base de datos.

```powershell
pipenv run python manage.py init-db
```

1. Migrar textos heredados a páginas, si aplica.

```powershell
pipenv run python manage.py migrate-texto-pages
```

1. Importar el dataset canónico desde `biblioteca/`.

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

## Paginación de textos

- El importador toma las páginas detectadas en `origen_md.md`.
- No hay objetivo fijo forzado de 16 o 32 páginas.
- Para usar 16 páginas, prepara el archivo fuente con ese total.

## Respaldo de prompts

- Exportar prompts desde SQLite a JSON.

```powershell
pipenv run python manage.py export-prompts
```

- Importar prompts desde JSON a SQLite.

```powershell
pipenv run python manage.py import-prompts
```

## Convención de códigos de cuento

- Código por libro: `2` dígitos numéricos (`01`, `02`, `03`, ...).
- El código no incluye el número del libro.
