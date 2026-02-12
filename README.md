# Cuentos Cosmere

Proyecto personal de cuentos ilustrados con flujo profesional.

## Arquitectura actual

- Fuente de verdad: archivos en `biblioteca/`.
- Contrato de cuento: `meta.md` + páginas `NNN.md`.
- Prompt y narrativa: solo edición en Markdown.
- Caché temporal: SQLite de lectura rápida (`db/library_cache.sqlite`).
- UI: navegación, copia de texto/prompt/referencias y guardado de imágenes por slot.

## Estructura canónica de cuento

```text
biblioteca/<ruta-nodos>/.../<cuento>/
  meta.md
  001.md
  002.md
  ...
  assets/
    imagenes/
      pagina-001-principal.png
  referencias/
    referencia_pdf.pdf
```

## Flujo recomendado

1. Migrar layout legacy (si aplica):
   `python manage.py migrate-library-layout --apply`
2. Reconstruir caché:
   `python manage.py rebuild-cache`
3. Abrir servidor cuando lo pidas explícitamente:
   `python manage.py runserver`

## Comandos clave

- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py rebuild-cache`
- `python manage.py import`

`import` queda como alias deprecado para migrar layout legacy y refrescar caché.

## Convenciones del repositorio

- Operación: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Contexto mínimo: `docs/context/`
