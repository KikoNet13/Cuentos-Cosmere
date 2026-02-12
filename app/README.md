# Cuentos Cosmere

Tecnologias:

- Flask
- Peewee
- SQLite
- HTMX

## Inicio rapido (Pipenv)

1. Instalar dependencias:

```powershell
pipenv install
```

2. Crear el esquema de base de datos:

```powershell
pipenv run python manage.py init-db
```

3. Si vienes del esquema anterior de textos, migrar a paginas:

```powershell
pipenv run python manage.py migrate-texto-pages
```

4. Importar dataset desde la biblioteca canonica:

```powershell
pipenv run python manage.py import
```

5. Ejecutar servidor de desarrollo:

```powershell
pipenv run python manage.py runserver --debug
```

6. Abrir en navegador:

`http://127.0.0.1:5000`

## Respaldo de prompts

- Exportar prompts desde SQLite a JSON:

```powershell
pipenv run python manage.py export-prompts
```

- Importar prompts desde JSON a SQLite:

```powershell
pipenv run python manage.py import-prompts
```

## Convencion de codigos de cuento

- Codigo por libro: `2` digitos numericos (`01`, `02`, `03`, ...).
- El codigo no incluye el numero de libro.
